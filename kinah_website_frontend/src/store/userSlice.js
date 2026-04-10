import { createSlice } from "@reduxjs/toolkit";


const data = {
  id: "d59824dd-5ae3-4722-970b-9707cbb555b6",
  first_name: "John",
  last_name: "Doe",
  email: "john.doe@example.com",
  phone: "+254712345678",
  role: {
    role_id: 2,
    role_name: "buyer",
    color: "#ee3b9d"
  },
  photo: null,
  is_active: true,
  is_staff: false,
  created_at: "2026-04-03T12:43:17.201366Z",
  updated_at: "2026-04-03T12:43:17.201438Z",
  shipping_address: {
    id: 1,
    address_type: "shipping",
    street_address: "Main St",
    apartment_address: '123',
    city: "Kosofe",
    state: "Lagos",
    postal_code: null,
    longitude: 3.3792, 
    latitude: 6.5244,
    country: "Nigeria"
  },
  billing_address: {
    id: 2,
    address_type: "billing",
    street_address: "Main St",
    apartment_address: '123',
    city: "Kosofe",
    state: "Lagos",
    postal_code: null,
    country: "Nigeria"
  },
  orders: [
    {
      id: "0a12d313-0c5d-4215-b89a-a850c258f215",
      order_number: "ORD-000001",
      user: "d59824dd-5ae3-4722-970b-9707cbb555b6",
      user_email: "john.doe@example.com",
      user_full_name: "John Doe",
      status: "processing",
      payment_status: "pending",
      payment_method: "paystack",
      total_amount: "0.00",
      item_count: 0,
      created_at: "2026-04-03T12:43:20.222164Z"
    }
  ],
  isLoggedIn: false
}


const initialState = {
  user: data,
  token: localStorage.getItem("token") || null,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    login: (state, action) => {
      state.user = action.payload.user;
      state.token = action.payload.token;

      localStorage.setItem("token", JSON.stringify(action.payload.token));
    },
    logout: (state) => {
      state.user = null;
      state.token = null;

      localStorage.removeItem("token");
    },
  },
});

export const { login, logout } = userSlice.actions;
export default userSlice.reducer;