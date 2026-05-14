import axios from "axios";
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
const api = axios.create({ baseURL: BASE });

export const uploadResume = async (file) => {
  const form = new FormData();
  form.append("file", file);
  return (await api.post("/ingest", form, {
    headers: { "Content-Type": "multipart/form-data" }
  })).data;
};

export const queryResumes = async (question, useAgent = false) =>
  (await api.post("/query", { question, use_agent: useAgent })).data;