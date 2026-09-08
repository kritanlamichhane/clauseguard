from backend.core.config import (
    BASE_DIR,
    DATA_DIR,
    UPLOAD_DIR,
    MODEL_DIR,
    DB_PATH,
    SECRET_KEY,
    GEMINI_API_KEY,
    ALLOWED_EXTENSIONS
)

from backend.core.models import (
    UserRegister,
    UserLogin,
    UserProfile,
    TokenResponse,
    Clause,
    ContractEntities,
    RiskBreakdown,
    RiskReport,
    HistorySummaryItem,
    HistoryDetailResponse
)

from backend.core.database import (
    get_db_connection,
    init_db,
    create_user,
    get_user_by_email,
    get_user_by_id,
    save_analysis_history,
    get_user_history,
    get_history_detail,
    delete_history_item
)

from backend.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token
)

from backend.core.dependencies import (
    get_current_user,
    get_optional_user
)

from backend.core.rate_limiter import (
    gemini_rate_limiter,
    RateLimitExceeded,
    SlidingWindowRateLimiter,
)
