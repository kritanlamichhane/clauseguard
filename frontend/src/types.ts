export type RiskLevel = 'high' | 'medium' | 'low' | 'safe';

export interface RuleMatch {
  rule_id: string;
  risk_type: string;
  risk_level: RiskLevel;
  pattern_matched: string;
}

export interface SimilarityMatch {
  risk_type: string;
  risk_level: RiskLevel;
  similarity_score: number;
  matched_reference: string;
}

export interface ClauseResult {
  clause_text: string;
  clause_type_predicted: string;
  risk_level: RiskLevel;
  risk_type: string;
  explanation: string;
  recommendation: string;
  rule_matches?: RuleMatch[];
  similarity_match?: SimilarityMatch | null;
}

export interface RiskBreakdown {
  high: number;
  medium: number;
  low: number;
  safe: number;
}

export interface Entities {
  parties: string[];
  dates: string[];
  amounts: string[];
  locations: string[];
}

export interface AnalysisResponse {
  file_name: string;
  total_clauses: number;
  risk_score: number;
  risk_label: string;
  risk_breakdown: RiskBreakdown;
  entities: Entities;
  summary: string;
  clauses: ClauseResult[];
  history_id?: number | null;
}

export interface User {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface HistoryItem {
  id: number;
  file_name: string;
  risk_score: number;
  risk_label: string;
  total_clauses: number;
  summary: string;
  created_at: string;
}

export interface HistoryDetailResponse extends AnalysisResponse {
  id: number;
  user_id: number;
  created_at: string;
}
