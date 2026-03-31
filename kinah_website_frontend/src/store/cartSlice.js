import { createSlice } from "@reduxjs/toolkit";
import productImage from '../assets/product_image.png'


const productData = {
    id: "4b01f7e3-3eff-4678-9197-c1a952b0224b",
    name: 'Givenchy Up and Down',
    price: 1800.0,
    image: productImage,
    quantity: 1
}

const savedItems = JSON.parse(localStorage.getItem('cart')) || []

const initialState = {
  // items: [
  //   productData, 
  //   {...productData, id: "4b01f7e3-3eff-4678-9197-c1a952b0226a"}, 
  //   {...productData, id: "4b01f7e3-3eff-4678-9197-c1a952b022i2"}, 
  //   {...productData, id: "4b01f7e3-3eff-4678-9197-c1a952b022qr"},
  // ],
  items: savedItems,
};

const cartSlice = createSlice({
  name: "cart",
  initialState,
  reducers: {
    addToCart: (state, action) => {
      const existing = state.items.find(
        (item) => item.id === action.payload.id
      );

      if (existing) {
        existing.quantity += 1;
      } else {
        state.items.push({ ...action.payload, quantity: 1 });
      }
    },

    decreaseQuantity: (state, action) => {
      const existing = state.items.find(
        (item) => item.id === action.payload
      );

      if (existing) {
        if (existing.quantity > 1) {
          existing.quantity -= 1;
        } else {
          state.items = state.items.filter(
            (item) => item.id !== action.payload
          );
        }
      }
    },

    removeFromCart: (state, action) => {
      state.items = state.items.filter(
        (item) => item.id !== action.payload
      );
    },

    clearCart: (state) => {
      state.items = [];
    },
  },
});

export const { addToCart, decreaseQuantity, removeFromCart, clearCart } = cartSlice.actions;
export default cartSlice.reducer;