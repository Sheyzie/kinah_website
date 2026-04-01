import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import productImage from '../assets/product_image.png'
import { dataProvider } from "../providers/dataProvider";

const productData = {
    id: "4b01f7e3-3eff-4678-9197-c1a952b0224b",
    name: 'Givenchy Up and Down',
    category: {
        "id": 1,
        "name": "Male",
        "color": "blue"
    },
    type: {
        "id": 1,
        "name": "Shirt",
        "color": "green"
    },
    package_type: "single",
    price: 2000,
    old_price: null,
    discount_type: "percent",
    discount_value: "10.00",
    currency: "NGN",
    description: 'This collection features Snoopy and his friends enjoying basketball in a vintage paenut Givenchy Up and Down',
    quantity: 89,
    sold: 0,
    created_at: "2026-03-29T10:37:24.340588Z",
    updated_at: "2026-03-29T10:37:24.340609Z",
    final_price: 1800.0,
    review_score: 0.0,
    images: [
        {
            id: 1,
            image: productImage,
            is_primary: true,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 2,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 3,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 4,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 5,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
    ]
}

const generateId = () =>
  crypto.randomUUID?.() ||
  Math.random().toString(36).substring(2) + Date.now();

const extraProducts = Array.from({ length: 20 }, () => ({
  ...productData,
  id: generateId(),
}));

const initialState = {
  products: [
    // productData,
    // ...extraProducts
  ],
  status: "idle", // idle | loading | succeeded | failed
  error: null,
};

const productSlice = createSlice({
  name: "products",
  initialState,
  reducers: {
    // setProducts: (state, action) => {
    //   state.products = action.payload;
    // },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => {
        state.status = "loading";
      })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.status = "succeeded";
        state.products = action.payload;
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.status = "failed";
        state.error = action.payload;
      });
  },
});

export const fetchProducts = createAsyncThunk(
  "products/fetchProducts",
  async (query, thunkAPI) => {
    try {
      // const { data } = await dataProvider.getList({resource: 'products', pagination: query.pagination, sorters: query.sorter, filters: query.filter})
      // return data
      return extraProducts
    } catch (error) {
      return thunkAPI.rejectWithValue(error.response?.data || error.message);
    }
  }
);

export const { setProducts } = productSlice.actions;
export default productSlice.reducer;