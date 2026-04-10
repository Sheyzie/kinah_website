import axios from "axios";

const BASE_URL = "http://localhost:8000/api/v1"

const axiosInstance = axios.create({
  baseURL: BASE_URL,
});

// ✅ INTERCEPTOR HERE
axiosInstance.interceptors.request.use(
  (config) => {
    const token = JSON.parse(localStorage.getItem("token")) || {};

    if (token) {
      config.headers.Authorization = `Bearer ${token.accessToken}`;
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      const token = JSON.parse(localStorage.getItem("token")) || {};

      
      if (token) {
        try{
          const response = await axios.post(`${BASE_URL}/token/refresh/`, {refresh: token.refreshToken})
          // get login reducer from user
        }
        catch (err) {
          // optional redirect
          window.location.href = "/auth/login";
        }
      }

      // optional redirect
      window.location.href = "/auth/login";
    }

    return Promise.reject(error);
  }
);


export default axiosInstance;