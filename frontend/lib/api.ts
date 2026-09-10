const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

type ApiErrorBody = { detail?: string };

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new Error(body?.detail ?? `Request failed with status ${res.status}`);
  }

  return res.json() as Promise<T>;
}

export type AuthResponse = { access_token: string; token_type: string };

export function signup(input: { name: string; email: string; password: string }) {
  return request<AuthResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function login(input: { email: string; password: string }) {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export type CurrentUser = {
  id: string;
  name: string;
  email: string;
  created_at: string;
};

export function getCurrentUser(token: string) {
  return request<CurrentUser>("/auth/me", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type ResumeStatus = "ready" | "failed";

export type ResumeRead = {
  id: string;
  original_filename: string;
  status: ResumeStatus;
  char_count: number | null;
  error_message: string | null;
  created_at: string;
};

export async function uploadResume(
  token: string,
  file: File
): Promise<ResumeRead> {
  const formData = new FormData();
  formData.append("file", file);

  // Not using request() here — it always sets Content-Type: application/json,
  // which would break the multipart boundary the browser needs to set itself.
  const res = await fetch(`${API_URL}/resumes`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!res.ok) {
    const body = (await res.json().catch(() => null)) as ApiErrorBody | null;
    throw new Error(body?.detail ?? `Upload failed with status ${res.status}`);
  }

  return res.json();
}

export function listResumes(token: string) {
  return request<ResumeRead[]>("/resumes", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type ExperienceEntry = {
  title: string;
  company: string;
  start_date: string | null;
  end_date: string | null;
  description: string[];
};

export type EducationEntry = {
  degree: string;
  institution: string;
  start_date: string | null;
  end_date: string | null;
};

export type ProjectEntry = {
  name: string;
  description: string[];
  technologies: string[];
};

export type CertificationEntry = {
  title: string | null;
  issuer: string | null;
  date: string | null;
};

export type CandidateProfileData = {
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: CertificationEntry[];
};

export type CandidateProfileResponse = {
  status: "ready" | "failed";
  data: CandidateProfileData | null;
  error_message: string | null;
};

export function parseResume(token: string, resumeId: string) {
  return request<CandidateProfileResponse>(`/resumes/${resumeId}/parse`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getCandidateProfile(token: string, resumeId: string) {
  return request<CandidateProfileResponse>(`/resumes/${resumeId}/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type JobRead = {
  id: string;
  title: string | null;
  company: string | null;
  raw_text: string;
  created_at: string;
};

export function createJob(
  token: string,
  input: { title?: string; company?: string; raw_text: string }
) {
  return request<JobRead>("/jobs", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify(input),
  });
}

export function listJobs(token: string) {
  return request<JobRead[]>("/jobs", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type JobProfileData = {
  required_skills: string[];
  preferred_skills: string[];
  min_years_experience: number | null;
  seniority: string | null;
  responsibilities: string[];
  education_requirements: string[];
};

export type JobProfileResponse = {
  status: "ready" | "failed";
  data: JobProfileData | null;
  error_message: string | null;
};

export function parseJob(token: string, jobId: string) {
  return request<JobProfileResponse>(`/jobs/${jobId}/parse`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}

export function getJobProfile(token: string, jobId: string) {
  return request<JobProfileResponse>(`/jobs/${jobId}/profile`, {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type SkillMatchDetail = {
  matched: string[];
  missing: string[];
  score: number;
};

export type ExperienceMatchDetail = {
  candidate_years: number;
  required_years: number | null;
  score: number;
};

export type ProjectMatchDetail = {
  matched_skills: string[];
  score: number;
};

export type EducationMatchDetail = {
  candidate_level: string | null;
  required_level: string | null;
  score: number;
};

export type MatchResult = {
  overall_score: number;
  required_skills: SkillMatchDetail;
  preferred_skills: SkillMatchDetail;
  experience: ExperienceMatchDetail;
  projects: ProjectMatchDetail;
  education: EducationMatchDetail;
  semantic_score: number;
  weights: Record<string, number>;
};

export type SkillGap = {
  skill: string;
  importance: "required" | "preferred";
  status: "matched" | "partial" | "missing";
  evidence: string | null;
  priority: number;
};

export type GapAnalysis = {
  gaps: SkillGap[];
};

export type AnalysisRead = {
  id: string;
  resume_id: string;
  job_id: string;
  overall_score: number;
  result: MatchResult;
  gap_analysis: GapAnalysis;
  created_at: string;
};

export function runAnalysis(token: string, resumeId: string, jobId: string) {
  return request<AnalysisRead>("/analyses", {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
  });
}

export function listAnalyses(token: string) {
  return request<AnalysisRead[]>("/analyses", {
    headers: { Authorization: `Bearer ${token}` },
  });
}

export type RoadmapItem = {
  skill: string;
  reason: string | null;
  priority: string | null;
  effort: string | null;
  practical_task: string | null;
};

export type RoadmapData = {
  items: RoadmapItem[];
};

export type RoadmapResponse = {
  status: "ready" | "failed";
  data: RoadmapData | null;
  error_message: string | null;
};

export function generateRoadmap(token: string, analysisId: string) {
  return request<RoadmapResponse>(`/analyses/${analysisId}/roadmap`, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
  });
}