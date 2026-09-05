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
  description: string | null;
};

export type EducationEntry = {
  degree: string;
  institution: string;
  start_date: string | null;
  end_date: string | null;
};

export type ProjectEntry = {
  name: string;
  description: string | null;
  technologies: string[];
};

export type CertificationEntry = {
  name: string;
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