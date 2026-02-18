from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field, HttpUrl, model_validator


# -------------------------
# Enums
# -------------------------

class RagMode(str, Enum):
    vanilla = "vanilla"
    agentic = "agentic"


class ToolKind(str, Enum):
    medlineplus = "medlineplus"
    google_places = "google_places"
    ns_virtualcare = "ns_virtualcare"
    mcp_remote = "mcp_remote"


class ApprovalType(str, Enum):
    fetch_more_pages = "fetch_more_pages"
    use_external_provider_lookup = "use_external_provider_lookup"
    use_remote_mcp_tool = "use_remote_mcp_tool"
    increase_token_budget = "increase_token_budget"


# -------------------------
# Guardrails
# -------------------------

class Guardrails(BaseModel):
    # Hard allowlist: do not fetch outside these domains.
    allowed_domains: List[str] = Field(
        default_factory=lambda: ["medlineplus.gov", "wsearch.nlm.nih.gov", "nlm.nih.gov"],
        description="Only allow HTTP retrieval from these domains."
    )

    # Safety: keep responses general, not diagnostic; minimize PHI collection/storage.
    allow_personal_data: bool = Field(default=False, description="If false, do not store user profile fields.")
    redact_sensitive_inputs: bool = Field(default=True, description="If true, redact/avoid storing sensitive text.")

    # Token and retrieval budgets (primary cost controls)
    max_topics: int = Field(default=5, ge=1, le=15)
    max_pages: int = Field(default=5, ge=1, le=20)
    max_chunks: int = Field(default=10, ge=1, le=40)
    max_chunk_chars: int = Field(default=3500, ge=500, le=12000)

    # LLM budget controls (soft but enforced by your code)
    max_prompt_tokens: int = Field(default=3500, ge=500, le=12000)
    max_answer_tokens: int = Field(default=600, ge=100, le=2000)

    # Retrieval behavior
    retrieve_k: int = Field(default=6, ge=1, le=12)
    require_multitopic_coverage: bool = Field(
        default=True,
        description="For questions with multiple conditions, require evidence for each if possible."
    )


# -------------------------
# HITL (Human-in-the-loop)
# -------------------------

class HitlPolicy(BaseModel):
    enabled: bool = Field(default=True)

    # Require explicit user approval for these actions.
    require_approval_for: List[ApprovalType] = Field(
        default_factory=lambda: [
            ApprovalType.fetch_more_pages,
            ApprovalType.use_external_provider_lookup,
            ApprovalType.use_remote_mcp_tool,
            ApprovalType.increase_token_budget,
        ]
    )

    # Thresholds that trigger approvals
    approval_threshold_pages: int = Field(default=5, ge=1, le=20)
    approval_threshold_prompt_tokens: int = Field(default=3500, ge=500, le=12000)

    # Store approvals in-memory per session (or persist if you want)
    approvals: Dict[str, bool] = Field(
        default_factory=dict,
        description="Map of approval keys -> approved bool."
    )

    def is_approved(self, key: str) -> bool:
        return bool(self.approvals.get(key, False))

    def set_approval(self, key: str, approved: bool) -> None:
        self.approvals[key] = approved


# -------------------------
# MCP (Model Context Protocol) configuration
# -------------------------

class McpServerConfig(BaseModel):
    name: str
    transport: Literal["stdio", "http"] = "http"
    url: Optional[str] = Field(default=None, description="e.g., http://localhost:8000/mcp")
    command: Optional[str] = Field(default=None, description="For stdio: command to start server")
    args: List[str] = Field(default_factory=list)

class ToolConfig(BaseModel):
    kind: ToolKind
    enabled: bool = True

    # Local tool config (e.g., API keys, toggles)
    config: Dict[str, Any] = Field(default_factory=dict)

    # If using MCP tool server
    mcp: Optional[McpServerConfig] = None


# -------------------------
# Runtime (Context)
# -------------------------

class UserContext(BaseModel):
  
    location_text: Optional[str] = Field(default=None, description="User-provided location like 'Halifax, NS'")
    radius_km: int = Field(default=10, ge=1, le=100)

    
    prefer_virtual: bool = False
    prefer_walk_in: bool = True
    prefer_pharmacy: bool = True
    mobility_constraints: bool = False


class RuntimeContext(BaseModel):
    mode: RagMode = RagMode.vanilla

    question: str = Field(..., min_length=5)
    user: UserContext = Field(default_factory=UserContext)

    guardrails: Guardrails = Field(default_factory=Guardrails)
    hitl: HitlPolicy = Field(default_factory=HitlPolicy)

    tools: List[ToolConfig] = Field(
        default_factory=lambda: [
            ToolConfig(kind=ToolKind.medlineplus, enabled=True),
            ToolConfig(kind=ToolKind.ns_virtualcare, enabled=True),
            ToolConfig(kind=ToolKind.google_places, enabled=False),
        ]
    )

   
    run_id: str = Field(default="run-001")
    debug_print_retrieval: bool = True

    @model_validator(mode="after")
    def validate_budgets(self) -> "RuntimeContext":
       
        if self.guardrails.retrieve_k > self.guardrails.max_chunks:
            self.guardrails.retrieve_k = self.guardrails.max_chunks
        return self


# -------------------------
# report schema 
# -------------------------

class RetrievedItem(BaseModel):
    source_url: Optional[HttpUrl] = None
    title: Optional[str] = None
    snippet: Optional[str] = None
    chunk_preview: Optional[str] = None

class RetrievalReport(BaseModel):
    run_id: str
    mode: RagMode
    question: str

    #  fetched / indexed / retrieved
    searched_topics: List[Dict[str, Any]] = Field(default_factory=list)
    fetched_urls_
