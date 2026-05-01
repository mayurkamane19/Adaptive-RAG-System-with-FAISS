from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, status
from pydantic import BaseModel, Field
from typing_extensions import Literal

from app.graph.langgraph_flow import run_adaptive_rag
from app.services.saas_store import (
    authenticate_user,
    clear_session,
    create_billing_item,
    create_notification_item,
    create_report_run,
    create_user,
    create_workspace_user,
    delete_billing_item,
    delete_notification_item,
    delete_report_run,
    delete_workspace_user,
    get_analytics_overview,
    get_billing_overview,
    get_dashboard_overview,
    get_notifications_overview,
    get_profile_overview,
    get_reports_overview,
    get_settings_overview,
    get_user_by_token,
    get_users_overview,
    require_role,
)


router = APIRouter(tags=["Adaptive RAG"])


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=2, examples=["What is adaptive RAG?"])


class QueryResponse(BaseModel):
    question: str
    route: str
    answer: str
    sources: list[str]
    rewritten_question: str
    self_correction_attempts: int
    vector_backend: str
    llm_backend: str


class AuthCredentials(BaseModel):
    email: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)


class SignupRequest(AuthCredentials):
    full_name: str = Field(..., min_length=2)


class UserResponse(BaseModel):
    full_name: str
    email: str
    role: str


class AuthResponse(BaseModel):
    token: str
    user: UserResponse


class MessageResponse(BaseModel):
    message: str


class DashboardStat(BaseModel):
    title: str
    value: str
    hint: str
    tone: Literal["default", "accent"]


class ChartBar(BaseModel):
    label: str
    value: int


class TableRow(BaseModel):
    id: str
    values: list[str]


class WorkspaceUserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    role: str = Field(..., min_length=2)
    status_value: str = Field(..., min_length=2, alias="status")
    region: str = Field(..., min_length=2)


class BillingItemCreateRequest(BaseModel):
    item: str = Field(..., min_length=2)
    amount: str = Field(..., min_length=2)
    status_value: str = Field(..., min_length=2, alias="status")
    invoice_date: str = Field(..., min_length=4)


class ReportRunCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    status_value: str = Field(..., min_length=2, alias="status")
    day_label: str = Field(..., min_length=2)


class NotificationItemCreateRequest(BaseModel):
    title: str = Field(..., min_length=2)
    detail: str = Field(..., min_length=4)


class DashboardHero(BaseModel):
    headline: str
    subtext: str
    arr_value: str | None = None
    arr_hint: str | None = None


class DashboardOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    growth_bars: list[ChartBar]
    accounts: list[TableRow]


class Point(BaseModel):
    x: int
    y: int


class AnalyticsOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    points: list[Point]


class TableOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    rows: list[TableRow]


class ReportsOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    bars: list[ChartBar]
    rows: list[TableRow]


class DetailItem(BaseModel):
    id: str | None = None
    title: str
    detail: str


class DetailOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    items: list[DetailItem]


class ProfileSummary(BaseModel):
    initials: str
    name: str
    role: str
    summary: str


class ProfileOverviewResponse(BaseModel):
    hero: DashboardHero
    stats: list[DashboardStat]
    profile: ProfileSummary


def extract_token(authorization: Annotated[str | None, Header()] = None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing bearer token.",
        )
    return authorization.replace("Bearer ", "", 1)


@router.post("/ask", response_model=QueryResponse)
def ask_question(payload: QueryRequest):
    result = run_adaptive_rag(payload.question)
    return QueryResponse(**result)


@router.post("/api/auth/signup", response_model=AuthResponse, tags=["SaaS Auth"])
def signup(payload: SignupRequest):
    user = create_user(payload.full_name, payload.email, payload.password)
    token, authenticated_user = authenticate_user(user["email"], payload.password)
    return AuthResponse(
        token=token,
        user=UserResponse(
            full_name=authenticated_user["full_name"],
            email=authenticated_user["email"],
            role=authenticated_user["role"],
        ),
    )


@router.post("/api/auth/login", response_model=AuthResponse, tags=["SaaS Auth"])
def login(payload: AuthCredentials):
    token, user = authenticate_user(payload.email, payload.password)
    return AuthResponse(
        token=token,
        user=UserResponse(
            full_name=user["full_name"],
            email=user["email"],
            role=user["role"],
        ),
    )


@router.get("/api/auth/me", response_model=UserResponse, tags=["SaaS Auth"])
def current_user(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return UserResponse(
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"],
    )


@router.post("/api/auth/logout", response_model=MessageResponse, tags=["SaaS Auth"])
def logout(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    clear_session(token)
    return MessageResponse(message="Logged out successfully.")


@router.get(
    "/api/dashboard/overview",
    response_model=DashboardOverviewResponse,
    tags=["SaaS Dashboard"],
)
def dashboard_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return DashboardOverviewResponse(**get_dashboard_overview(user))


@router.get(
    "/api/analytics/overview",
    response_model=AnalyticsOverviewResponse,
    tags=["SaaS Analytics"],
)
def analytics_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return AnalyticsOverviewResponse(**get_analytics_overview(user))


@router.get(
    "/api/users/overview",
    response_model=TableOverviewResponse,
    tags=["SaaS Users"],
)
def users_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return TableOverviewResponse(**get_users_overview(user))


@router.get(
    "/api/reports/overview",
    response_model=ReportsOverviewResponse,
    tags=["SaaS Reports"],
)
def reports_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return ReportsOverviewResponse(**get_reports_overview(user))


@router.get(
    "/api/billing/overview",
    response_model=TableOverviewResponse,
    tags=["SaaS Billing"],
)
def billing_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return TableOverviewResponse(**get_billing_overview(user))


@router.post("/api/users/members", response_model=MessageResponse, tags=["SaaS Users"])
def add_workspace_user(
    payload: WorkspaceUserCreateRequest,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    require_role(user, "admin")
    create_workspace_user(int(user["id"]), payload.name, payload.role, payload.status_value, payload.region)
    return MessageResponse(message="Workspace user created successfully.")


@router.delete(
    "/api/users/members/{member_id}",
    response_model=MessageResponse,
    tags=["SaaS Users"],
)
def remove_workspace_user(
    member_id: int,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    require_role(user, "admin")
    delete_workspace_user(int(user["id"]), member_id)
    return MessageResponse(message="Workspace user removed successfully.")


@router.post("/api/billing/items", response_model=MessageResponse, tags=["SaaS Billing"])
def add_billing_item(
    payload: BillingItemCreateRequest,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    require_role(user, "admin")
    create_billing_item(
        int(user["id"]),
        payload.item,
        payload.amount,
        payload.status_value,
        payload.invoice_date,
    )
    return MessageResponse(message="Billing item created successfully.")


@router.delete(
    "/api/billing/items/{item_id}",
    response_model=MessageResponse,
    tags=["SaaS Billing"],
)
def remove_billing_item(
    item_id: int,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    require_role(user, "admin")
    delete_billing_item(int(user["id"]), item_id)
    return MessageResponse(message="Billing item removed successfully.")


@router.post("/api/reports/runs", response_model=MessageResponse, tags=["SaaS Reports"])
def add_report_run(
    payload: ReportRunCreateRequest,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    create_report_run(int(user["id"]), payload.name, payload.status_value, payload.day_label)
    return MessageResponse(message="Report run created successfully.")


@router.delete(
    "/api/reports/runs/{report_id}",
    response_model=MessageResponse,
    tags=["SaaS Reports"],
)
def remove_report_run(
    report_id: int,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    delete_report_run(int(user["id"]), report_id)
    return MessageResponse(message="Report run removed successfully.")


@router.post(
    "/api/notifications/items",
    response_model=MessageResponse,
    tags=["SaaS Notifications"],
)
def add_notification_item(
    payload: NotificationItemCreateRequest,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    create_notification_item(int(user["id"]), payload.title, payload.detail)
    return MessageResponse(message="Notification item created successfully.")


@router.delete(
    "/api/notifications/items/{notification_id}",
    response_model=MessageResponse,
    tags=["SaaS Notifications"],
)
def remove_notification_item(
    notification_id: int,
    authorization: Annotated[str | None, Header()] = None,
):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    delete_notification_item(int(user["id"]), notification_id)
    return MessageResponse(message="Notification item removed successfully.")


@router.get(
    "/api/notifications/overview",
    response_model=DetailOverviewResponse,
    tags=["SaaS Notifications"],
)
def notifications_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return DetailOverviewResponse(**get_notifications_overview(user))


@router.get(
    "/api/settings/overview",
    response_model=DetailOverviewResponse,
    tags=["SaaS Settings"],
)
def settings_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    get_user_by_token(token)
    return DetailOverviewResponse(**get_settings_overview())


@router.get(
    "/api/profile/overview",
    response_model=ProfileOverviewResponse,
    tags=["SaaS Profile"],
)
def profile_overview(authorization: Annotated[str | None, Header()] = None):
    token = extract_token(authorization)
    user = get_user_by_token(token)
    return ProfileOverviewResponse(**get_profile_overview(user))
