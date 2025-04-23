from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional, Dict, Any
import sqlite3
import os
import json
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext

# 创建FastAPI实例
app = FastAPI(title="业财融合管理系统API", description="业财融合管理系统的后端API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源，生产环境应该设置为特定的来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置JWT认证
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 数据库路径
DATABASE_PATH = os.path.join("..", "database", "finance.db")

# 数据模型
class User(BaseModel):
    id: Optional[int] = None
    username: str
    role: str
    department: str
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class BusinessEvent(BaseModel):
    id: Optional[int] = None
    event_type: str
    project_name: str
    project_code: Optional[str] = None
    amount: float
    event_date: str
    description: Optional[str] = None
    department_id: int
    created_by: int
    status: str = "待审批"
    customer_id: Optional[int] = None

class FinancialRecord(BaseModel):
    id: Optional[int] = None
    business_event_id: int
    account_code: str
    account_name: str
    amount: float
    direction: str
    record_date: str
    fiscal_year: int
    fiscal_period: int
    description: Optional[str] = None
    created_by: int

class StatusHistory(BaseModel):
    timestamp: str
    status: str
    operator: str
    remarks: Optional[str] = None

class BusinessEventDetail(BaseModel):
    id: int
    event_type: str
    project_name: str
    project_code: Optional[str] = None
    amount: float
    event_date: str
    description: Optional[str] = None
    department_id: int
    created_by: int
    status: str
    created_at: str
    approval_id: Optional[int] = None
    finance_id: Optional[int] = None
    status_history: Optional[List[StatusHistory]] = None

# 数据库连接函数
def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 验证用户
def verify_password(plain_password, hashed_password):
    # 简化版本：仅比较明文密码
    return plain_password == hashed_password

def get_user(username: str):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()
    if user:
        return dict(user)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user["password"]):
        return False
    return user

# 创建访问Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# 认证接口
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user = Depends(get_current_user)):
    return current_user

# 业务事件API
@app.get("/business_events")
async def get_business_events(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    events = conn.execute("SELECT * FROM business_events ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(event) for event in events]

@app.get("/business_events/{event_id}")
async def get_business_event(event_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    event = conn.execute("SELECT * FROM business_events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    if event is None:
        raise HTTPException(status_code=404, detail="业务事件不存在")
    return dict(event)

@app.post("/business_events")
async def create_business_event(event: BusinessEvent, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 生成唯一事务编号
    # 格式: 事件类型缩写-年月日-4位序号
    # 例如: XS-20230615-0001 (销售-2023年6月15日-0001号)

    # 获取当前日期
    current_date = datetime.now()
    date_str = current_date.strftime("%Y%m%d")

    # 事件类型映射
    event_type_map = {
        "销售": "XS",
        "采购": "CG",
        "合同": "HT",
        "报销": "BX"
    }

    # 获取事件类型缩写
    event_type_code = event_type_map.get(event.event_type, "QT")  # 默认为"其他"

    # 查询当天最大序号
    max_seq_query = """
        SELECT MAX(SUBSTR(project_code, -4)) as max_seq
        FROM business_events
        WHERE project_code LIKE ?
    """
    cursor.execute(max_seq_query, (f"{event_type_code}-{date_str}-%",))
    result = cursor.fetchone()
    
    # 添加调试输出
    print(f"SQL查询: {max_seq_query}")
    print(f"查询参数: {event_type_code}-{date_str}-%")
    print(f"查询结果: {result}")

    # 确定新序号
    if result and result["max_seq"]:
        next_seq = int(result["max_seq"]) + 1
    else:
        next_seq = 1
    
    # 生成完整事务编号
    transaction_code = f"{event_type_code}-{date_str}-{next_seq:04d}"
    
    # 添加调试输出
    print(f"生成的事务编号: {transaction_code}")

    # 将生成的事务编号赋值给 project_code
    event.project_code = transaction_code
    
    # 插入业务事件
    cursor.execute("""
        INSERT INTO business_events (event_type, project_name, project_code, amount, event_date, 
        description, department_id, created_by, status, customer_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (event.event_type, event.project_name, event.project_code, event.amount, 
          event.event_date, event.description, event.department_id, current_user["id"], "待审批", event.customer_id))
    
    event_id = cursor.lastrowid
    
    # 创建审批流程
    cursor.execute("""
        INSERT INTO approvals (business_event_id, approver_id, approval_level, status)
        SELECT ?, approver_id, approval_level, '待审批'
        FROM approval_configs
        WHERE event_type = ? AND department_id = ? AND is_active = 1
        AND (amount_threshold IS NULL OR amount_threshold <= ?)
        ORDER BY approval_level
    """, (event_id, event.event_type, event.department_id, event.amount))
    
    conn.commit()
    conn.close()
    
    # 添加调试输出
    print(f"事件ID: {event_id}")
    print(f"返回数据: {{'id': {event_id}, 'transaction_code': '{transaction_code}', 'message': '业务事件创建成功'}}")
    
    # 确保返回的数据结构清晰
    return {
        "id": event_id, 
        "transaction_code": transaction_code, 
        "message": "业务事件创建成功"
    }
    
@app.get("/customers")
async def get_customers(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    customers = conn.execute("SELECT * FROM customers ORDER BY name").fetchall()
    conn.close()
    return [dict(customer) for customer in customers]

# 财务记录API
@app.get("/financial_records")
async def get_financial_records(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    records = conn.execute("""
        SELECT fr.*, be.project_name, be.event_type
        FROM financial_records fr
        JOIN business_events be ON fr.business_event_id = be.id
        ORDER BY fr.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(record) for record in records]

@app.get("/financial_records/{record_id}")
async def get_financial_record(record_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    record = conn.execute("SELECT * FROM financial_records WHERE id = ?", (record_id,)).fetchone()
    conn.close()
    if record is None:
        raise HTTPException(status_code=404, detail="财务记录不存在")
    return dict(record)

@app.post("/financial_records")
async def create_financial_record(record: FinancialRecord, current_user = Depends(get_current_user)):
    # 检查用户是否有财务角色
    if current_user["role"] != "财务人员" and current_user["role"] != "管理员":
        raise HTTPException(status_code=403, detail="没有权限创建财务记录")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查关联的业务事件是否存在且已审批
    event = cursor.execute("SELECT * FROM business_events WHERE id = ?", 
                          (record.business_event_id,)).fetchone()
    if not event:
        conn.close()
        raise HTTPException(status_code=404, detail="关联的业务事件不存在")
    
    if dict(event)["status"] != "已审批":
        conn.close()
        raise HTTPException(status_code=400, detail="关联的业务事件尚未审批通过")
    
    # 插入财务记录
    cursor.execute("""
        INSERT INTO financial_records (business_event_id, account_code, account_name, 
        amount, direction, record_date, fiscal_year, fiscal_period, description, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (record.business_event_id, record.account_code, record.account_name, 
          record.amount, record.direction, record.record_date, record.fiscal_year, 
          record.fiscal_period, record.description, current_user["id"]))
    
    # 更新预算使用情况
    if record.direction == "支出":
        cursor.execute("""
            UPDATE budgets
            SET used_amount = used_amount + ?
            WHERE department_id = (SELECT department_id FROM business_events WHERE id = ?)
            AND year = ? AND month = ?
        """, (record.amount, record.business_event_id, record.fiscal_year, record.fiscal_period))
    
    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return {"id": record_id, "message": "财务记录创建成功"}

# 审批API
@app.get("/approvals")
async def get_approvals(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    
    # 管理员可以查看所有审批
    if current_user["role"] == "管理员":
        approvals = conn.execute("""
            SELECT a.*, be.project_name, be.event_type, be.amount, u.username as approver_name
            FROM approvals a
            JOIN business_events be ON a.business_event_id = be.id
            JOIN users u ON a.approver_id = u.id
            ORDER BY a.created_at DESC
        """).fetchall()
    else:
        # 普通用户只能查看自己的待审批记录
        approvals = conn.execute("""
            SELECT a.*, be.project_name, be.event_type, be.amount, u.username as approver_name
            FROM approvals a
            JOIN business_events be ON a.business_event_id = be.id
            JOIN users u ON a.approver_id = u.id
            WHERE a.approver_id = ? AND a.status = '待审批'
            ORDER BY a.created_at DESC
        """, (current_user["id"],)).fetchall()
    
    conn.close()
    return [dict(approval) for approval in approvals]

@app.post("/approvals/{approval_id}/approve")
async def approve(approval_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 验证审批流程是否存在
    approval = cursor.execute("""
        SELECT a.*, e.id as event_id, e.status as event_status 
        FROM approvals a
        JOIN business_events e ON a.business_event_id = e.id
        WHERE a.id = ?
    """, (approval_id,)).fetchone()
    
    if not approval:
        conn.close()
        raise HTTPException(status_code=404, detail="审批记录不存在")
    
    # 验证用户是否有权限审批
    if approval["approver_id"] != current_user["id"] and current_user["role"] != "管理员":
        conn.close()
        raise HTTPException(status_code=403, detail="您没有权限执行此审批")
    
    # 检查审批流程状态
    if approval["status"] != "待审批":
        conn.close()
        raise HTTPException(status_code=400, detail="此审批已处理，无法重复操作")
    
    # 更新审批状态
    cursor.execute(
        "UPDATE approvals SET status = '已通过', approved_at = datetime('now') WHERE id = ?",
        (approval_id,)
    )
    
    # 检查是否有下一级审批
    next_approval = cursor.execute("""
        SELECT id FROM approvals 
        WHERE business_event_id = ? AND approval_level > ? AND status = '待审批'
        ORDER BY approval_level LIMIT 1
    """, (approval["business_event_id"], approval["approval_level"])).fetchone()
    
    # 根据是否有下一级审批更新业务事件状态
    if next_approval:
        # 还有下一级审批，业务事件状态保持"审批中"
        new_status = "审批中"
    else:
        # 所有审批已完成，业务事件状态更新为"已审批"
        new_status = "已审批"
    
    # 更新业务事件状态
    cursor.execute(
        "UPDATE business_events SET status = ? WHERE id = ?",
        (new_status, approval["business_event_id"])
    )
    
    # 记录状态变更历史（如果有状态历史表）
    try:
        cursor.execute("""
            INSERT INTO status_history (business_event_id, timestamp, status, operator, remarks)
            VALUES (?, datetime('now'), ?, ?, '审批通过')
        """, (approval["business_event_id"], new_status, current_user["username"]))
    except:
        # 如果没有状态历史表，则忽略此步骤
        pass
    
    conn.commit()
    conn.close()
    
    return {"message": "审批已通过", "next_approval": next_approval is not None}

@app.post("/approvals/{approval_id}/reject")
async def reject(approval_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 验证审批流程是否存在
    approval = cursor.execute("""
        SELECT a.*, e.id as event_id 
        FROM approvals a
        JOIN business_events e ON a.business_event_id = e.id
        WHERE a.id = ?
    """, (approval_id,)).fetchone()
    
    if not approval:
        conn.close()
        raise HTTPException(status_code=404, detail="审批记录不存在")
    
    # 验证用户是否有权限审批
    if approval["approver_id"] != current_user["id"] and current_user["role"] != "管理员":
        conn.close()
        raise HTTPException(status_code=403, detail="您没有权限执行此审批")
    
    # 检查审批流程状态
    if approval["status"] != "待审批":
        conn.close()
        raise HTTPException(status_code=400, detail="此审批已处理，无法重复操作")
    
    # 更新审批状态
    cursor.execute(
        "UPDATE approvals SET status = '已拒绝', approved_at = datetime('now') WHERE id = ?",
        (approval_id,)
    )
    
    # 更新业务事件状态为"已拒绝"
    cursor.execute(
        "UPDATE business_events SET status = '已拒绝' WHERE id = ?",
        (approval["business_event_id"],)
    )
    
    # 记录状态变更历史（如果有状态历史表）
    try:
        cursor.execute("""
            INSERT INTO status_history (business_event_id, timestamp, status, operator, remarks)
            VALUES (?, datetime('now'), '已拒绝', ?, '审批拒绝')
        """, (approval["business_event_id"], current_user["username"]))
    except:
        # 如果没有状态历史表，则忽略此步骤
        pass
    
    conn.commit()
    conn.close()
    
    return {"message": "审批已拒绝"}

# 预算API
@app.get("/budgets")
async def get_budgets(year: int = None, month: int = None, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    query = """
        SELECT b.*, d.name as department_name, a.name as account_name
        FROM budgets b
        JOIN departments d ON b.department_id = d.id
        LEFT JOIN account_subjects a ON b.account_subject_id = a.id
    """
    params = []
    
    if year:
        query += " WHERE b.year = ?"
        params.append(year)
        if month:
            query += " AND b.month = ?"
            params.append(month)
    
    query += " ORDER BY b.year DESC, b.month DESC"
    
    budgets = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(budget) for budget in budgets]

@app.get("/departments")
async def get_departments(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    departments = conn.execute("SELECT * FROM departments").fetchall()
    conn.close()
    return [dict(dept) for dept in departments]

@app.get("/account_subjects")
async def get_account_subjects(current_user = Depends(get_current_user)):
    conn = get_db_connection()
    subjects = conn.execute("SELECT * FROM account_subjects").fetchall()
    conn.close()
    return [dict(subject) for subject in subjects]

# 获取业务事件详情（包含关联信息和状态历史）
@app.get("/business_events/{event_id}/detail", response_model=BusinessEventDetail)
async def get_business_event_detail(event_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取业务事件基本信息
    event = conn.execute("SELECT * FROM business_events WHERE id = ?", (event_id,)).fetchone()
    if event is None:
        conn.close()
        raise HTTPException(status_code=404, detail="业务事件不存在")
    
    event_data = dict(event)
    
    # 获取关联的审批信息
    approval = conn.execute("""
        SELECT id FROM approvals 
        WHERE business_event_id = ? 
        ORDER BY approval_level DESC LIMIT 1
    """, (event_id,)).fetchone()
    
    if approval:
        event_data["approval_id"] = approval["id"]
    
    # 获取关联的财务记录
    finance = conn.execute("""
        SELECT id FROM financial_records 
        WHERE business_event_id = ? 
        LIMIT 1
    """, (event_id,)).fetchone()
    
    if finance:
        event_data["finance_id"] = finance["id"]
    
    # 获取状态历史（示例：实际中应从状态历史表中获取）
    # 注意：这里假设有一个status_history表，如果没有，则需要通过其他方式模拟
    try:
        history = conn.execute("""
            SELECT * FROM status_history 
            WHERE business_event_id = ? 
            ORDER BY timestamp
        """, (event_id,)).fetchall()
        
        if history:
            event_data["status_history"] = [dict(record) for record in history]
        else:
            # 如果没有历史记录，创建一个基本的历史记录
            event_data["status_history"] = [{
                "timestamp": event_data["created_at"],
                "status": "新建",
                "operator": "系统",
                "remarks": "业务事件创建"
            }]
    except:
        # 如果没有状态历史表，则不返回历史记录
        event_data["status_history"] = []
    
    conn.close()
    return event_data

# 获取业务事件状态
@app.get("/business_events/{event_id}/status")
async def get_business_event_status(event_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    event = conn.execute("SELECT status FROM business_events WHERE id = ?", (event_id,)).fetchone()
    conn.close()
    
    if event is None:
        raise HTTPException(status_code=404, detail="业务事件不存在")
    
    return {"status": event["status"]}

# 获取业务事件关联数据
@app.get("/business_events/{event_id}/related")
async def get_business_event_related(event_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 查询关联的审批记录
    approvals = cursor.execute("""
        SELECT a.id, a.status, a.approval_level, a.approver_id, a.created_at, u.username as approver_name
        FROM approvals a
        LEFT JOIN users u ON a.approver_id = u.id
        WHERE a.business_event_id = ?
        ORDER BY a.approval_level
    """, (event_id,)).fetchall()
    
    # 查询关联的财务记录
    financial_records = cursor.execute("""
        SELECT id, account_name, amount, direction, record_date
        FROM financial_records
        WHERE business_event_id = ?
    """, (event_id,)).fetchall()
    
    conn.close()
    
    return {
        "approvals": [dict(a) for a in approvals] if approvals else [],
        "financial_records": [dict(f) for f in financial_records] if financial_records else []
    }

# 提交业务事件到审批流程
@app.post("/business_events/{event_id}/submit-to-approval")
async def submit_to_approval(event_id: int, current_user = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查业务事件是否存在
    event = cursor.execute("SELECT * FROM business_events WHERE id = ?", (event_id,)).fetchone()
    if not event:
        conn.close()
        raise HTTPException(status_code=404, detail="业务事件不存在")
    
    event_data = dict(event)
    
    # 检查当前状态是否允许提交审批
    if event_data["status"] not in ["新建", "待审批"]:
        conn.close()
        raise HTTPException(status_code=400, detail="当前状态不允许提交审批")
    
    # 创建审批任务（如果尚未创建）
    existing_approvals = cursor.execute(
        "SELECT COUNT(*) as count FROM approvals WHERE business_event_id = ?", 
        (event_id,)
    ).fetchone()
    
    if existing_approvals["count"] == 0:
        # 创建审批流程
        cursor.execute("""
            INSERT INTO approvals (business_event_id, approver_id, approval_level, status)
            SELECT ?, approver_id, approval_level, '待审批'
            FROM approval_configs
            WHERE event_type = ? AND department_id = ? AND is_active = 1
            AND (amount_threshold IS NULL OR amount_threshold <= ?)
            ORDER BY approval_level
        """, (event_id, event_data["event_type"], event_data["department_id"], event_data["amount"]))
    
    # 更新业务事件状态
    cursor.execute(
        "UPDATE business_events SET status = '待审批' WHERE id = ?",
        (event_id,)
    )
    
    # 记录状态变更历史（如果有状态历史表）
    try:
        cursor.execute("""
            INSERT INTO status_history (business_event_id, timestamp, status, operator, remarks)
            VALUES (?, datetime('now'), '待审批', ?, '提交到审批流程')
        """, (event_id, current_user["username"]))
    except:
        # 如果没有状态历史表，则忽略此步骤
        pass
    
    conn.commit()
    conn.close()
    
    return {"message": "业务事件已成功提交到审批流程"}

# 更新关联业务事件状态（供审批流程使用）
@app.post("/approvals/{approval_id}/update-business-status")
async def update_business_status(
    approval_id: int, 
    status_data: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    new_status = status_data.get("status")
    remarks = status_data.get("remarks", "")
    
    if not new_status:
        raise HTTPException(status_code=400, detail="缺少状态参数")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取关联的业务事件ID
    approval = cursor.execute(
        "SELECT business_event_id FROM approvals WHERE id = ?", 
        (approval_id,)
    ).fetchone()
    
    if not approval:
        conn.close()
        raise HTTPException(status_code=404, detail="审批记录不存在")
    
    business_event_id = approval["business_event_id"]
    
    # 更新业务事件状态
    cursor.execute(
        "UPDATE business_events SET status = ? WHERE id = ?",
        (new_status, business_event_id)
    )
    
    # 记录状态变更历史（如果有状态历史表）
    try:
        cursor.execute("""
            INSERT INTO status_history (business_event_id, timestamp, status, operator, remarks)
            VALUES (?, datetime('now'), ?, ?, ?)
        """, (business_event_id, new_status, current_user["username"], remarks))
    except:
        # 如果没有状态历史表，则忽略此步骤
        pass
    
    conn.commit()
    conn.close()
    
    return {"message": f"业务事件状态已更新为 {new_status}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 