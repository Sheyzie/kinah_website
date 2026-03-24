import axiosInstance from "../utils/axiosInstance";

const API_URL = "http://localhost:8000/api";

export const dataProvider = {
    getList: async ({ resource, pagination, filters, sorters }) => {
    const { current = 1, pageSize = 10 } = pagination || {};

    let query = `?page=${current}&page_size=${pageSize}`;

    // Filters
    if (filters && filters.length > 0) {
      filters.forEach((filter) => {
        if (filter.value !== undefined && filter.value !== null) {
          query += `&${filter.field}=${filter.value}`;
        }
      });
    }

    // Sorting (DRF uses ordering=field or -field)
    if (sorters && sorters.length > 0) {
      const sorter = sorters[0]; // refine usually sends array
      const order = sorter.order === "desc" ? `-${sorter.field}` : sorter.field;
      query += `&ordering=${order}`;
    }

    const response = await axiosInstance.get(`/${resource}/${query}`);

    return {
      data: response.data.results,
      total: response.data.count,
    };
  },

  getOne: async ({ resource, id }) => {
    const response = await axiosInstance.get(`${API_URL}/${resource}/${id}/`);

    return {
      data: response.data,
    };
  },

  create: async ({ resource, variables }) => {
    const response = await axiosInstance.post(
      `${API_URL}/${resource}/`,
      variables
    );

    return {
      data: response.data,
    };
  },

  update: async ({ resource, id, variables }) => {
    const response = await axiosInstance.put(
      `${API_URL}/${resource}/${id}/`,
      variables
    );

    return {
      data: response.data,
    };
  },

  deleteOne: async ({ resource, id }) => {
    await axiosInstance.delete(`${API_URL}/${resource}/${id}/`);

    return {
      data: { id },
    };
  },
};
