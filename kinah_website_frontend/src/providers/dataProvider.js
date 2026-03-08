import { DataProvider } from "@refinedev/core";

const API_URL = "https://api.example.com";

export const dataProvider: DataProvider = {
  getList: async ({ resource }) => {
    const res = await fetch(`${API_URL}/${resource}`);
    const data = await res.json();

    return {
      data,
      total: data.length,
    };
  },

  getOne: async ({ resource, id }) => {
    const res = await fetch(`${API_URL}/${resource}/${id}`);
    const data = await res.json();

    return { data };
  },

  create: async ({ resource, variables }) => {
    const res = await fetch(`${API_URL}/${resource}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });

    const data = await res.json();
    return { data };
  },

  update: async ({ resource, id, variables }) => {
    const res = await fetch(`${API_URL}/${resource}/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(variables),
    });

    const data = await res.json();
    return { data };
  },

  deleteOne: async ({ resource, id }) => {
    await fetch(`${API_URL}/${resource}/${id}`, {
      method: "DELETE",
    });

    return { data: { id } };
  },

  custom: async ({ url, method, payload, query, headers }) => {
    const queryString = query
      ? `?${new URLSearchParams(query).toString()}`
      : "";

    const res = await fetch(`${API_URL}${url}${queryString}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...headers,
      },
      body: payload ? JSON.stringify(payload) : undefined,
    });

    const data = await res.json();
    return { data };
  },
};
