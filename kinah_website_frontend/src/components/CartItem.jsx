import { Card, CardMedia, IconButton, Stack } from "@mui/material"
import DeleteIcon from '@mui/icons-material/Delete';
import productImage from '../assets/product_image.png'
import { PrimaryBtn } from "../components/Buttons";
import { useState } from "react";
import { useDispatch } from "react-redux";
import { addToCart, removeFromCart, decreaseQuantity, clearCart } from "../store/cartSlice";
import { formatToCurrency } from "../utils/formatToCurrency";


export default function CartItem({ item, setCartItems }) {

    const [cartItem, setCartItem] = useState(item)
    const dispatch = useDispatch()

    if(!cartItem) return

    const handleInputChange = (e) => {
        const newValue = Number(e.target.value);
        setCartItem(prevItem => ({...prevItem, quantity: newValue}))
        setCartItems(prevItems => prevItems.map(item => {
            if (item.id === cartItem.id) {
                return {...item, quantity: newValue}
            } else {
                return item
            }
        }))
        if (cartItem.quantity < newValue) {
            dispatch(addToCart(cartItem))
        } else {
            dispatch(decreaseQuantity(cartItem.id))
        }
        
    }
    const reduceQuantity = (e) => {
        if (cartItem.quantity == 1) return
        setCartItem(prevItem => ({...prevItem, quantity: prevItem.quantity - 1}))
        setCartItems(prevItems => prevItems.map(item => {
            if (item.id === cartItem.id) {
                return {...item, quantity: cartItem.quantity - 1}
            } else {
                return item
            }
        }))
        dispatch(decreaseQuantity(cartItem.id))
    }

    const increaseQuantity = (e) => {
        setCartItem(prevItem => ({...prevItem, quantity: prevItem.quantity + 1}))
        setCartItems(prevItems => prevItems.map(item => {
            if (item.id === cartItem.id) {
                return {...item, quantity: cartItem.quantity + 1}
            } else {
                return item
            }
        }))
        dispatch(addToCart(cartItem))
    }

    return (
        <Card sx={{height: 'fit-content', paddingBottom: 2}}>
            <Stack direction='row' spacing={2} padding={{xs: 1, sm: 2}} sx={{height: 'fit-content'}}>
                <CardMedia 
                    component="img"
                    image={productImage}
                    alt="product"
                    sx={{objectFit: 'contain', width: {xs: '50px', sm: '100px'}, objectPosition: 'top'}}
                />
                <Stack position='relative' width='100%' spacing={1}>
                    <h3 className="max-w-35 sm:max-w-2xl font-bold">{cartItem.name}</h3>
                    <h3 className="font-bold text-2xl">{formatToCurrency(cartItem.price)}</h3>
                    <div className="flex align-middle gap-2 my-2" >
                        <div className="w-16 h-5 inline">
                            <PrimaryBtn text="-" action={reduceQuantity} />
                        </div>
                        <div className="w-6 h-5 inline">
                            <input value={cartItem.quantity} onChange={handleInputChange} type="text" className="w-full h-full outline outline-(--outline-color) rounded text-center text-sm" />
                        </div>
                        <div className="w-16 h-5 inline">
                            <PrimaryBtn text="+" action={increaseQuantity} />
                        </div>
                    </div>
                    <IconButton 
                        aria-label="delete" 
                        color="error" 
                        onClick={() => {
                            setCartItems(prevItems => prevItems.filter(prevItem => prevItem.id !== cartItem.id))
                            dispatch(removeFromCart(cartItem.id))
                            setCartItem(null)
                        }}
                        sx={{position: 'absolute', right: 0, top: 0}}
                        >
                        <DeleteIcon />
                    </IconButton>
                </Stack>
            </Stack>
        </Card>
    )
}