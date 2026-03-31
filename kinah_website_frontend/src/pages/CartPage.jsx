import { Button, Card, CardMedia, Container, Grid, IconButton, Paper, Stack, TextField } from "@mui/material"
import DeleteIcon from '@mui/icons-material/Delete';
import productImage from '../assets/product_image.png'
import { PrimaryBtn, SecondaryBtn } from "../components/Buttons";
import CartItem from "../components/CartItem";
import { useSelector } from "react-redux";
import { useState } from "react";
import { useDispatch } from "react-redux";
import { clearCart } from "../store/cartSlice";


function CartPage(){
    const items = useSelector((state) => state.cart.items) || [];
    const [cartItems, setCartItems] = useState(items)
    const dispatch = useDispatch()

    let subtotal = cartItems.reduce((total, item) => total + (Number(item.price) * Number(item.quantity)), 0)

    let discount = 0
    let delivery = 0
    const total = (subtotal - discount) + delivery

    if (cartItems.length == 0) {
        return (
            <>
            <div className="h-screen overflow-hidden">
                <Stack justifyContent='center' alignItems='center' size={{ xs: 12, sm: 6 , md: 9}} width='100%' height='100%'>   
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '250px', height: '200px'}}>
                        <div className="flex flex-col justify-center items-center gap-5 overflow-hidden">
                            <h3>0 item in cart</h3>
                            <p>Add item to cart now</p>
                            <div className="w-60 h-10">
                                <PrimaryBtn text='Check out some items' />
                            </div>
                        </div>
                    </Paper>
                </Stack>
            </div>
            </>
        )
    }
    return (
        <>
        <section className='mb-10 mt-25 h-max md:h-[75vh]'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
                        <Stack spacing={1}>
                            <h3 className="font-bold">Your cart</h3>
                            <p className="text-(--outline-color)">Track stock level, availability and restocking needs in real-time</p>

                            <Stack direction={{xs: 'column', sm: 'column', md: 'row'}} spacing={5} >
                                <Paper elevation={3} sx={{ p: {xs: 2, sm: 3}, borderRadius: 3, height: 'fit-content', maxHeight: '450px', overflowY: 'scroll'}}>
                                    <Stack spacing={2} width={{xs: '100%', sm: '100%', md: 450, lg: 600}} >
                                        {items.map(item => (
                                            <CartItem key={item.id} item={item} setCartItems={setCartItems} />
                                        ))}
                                    </Stack>
                                </Paper>

                                <Paper elevation={3} sx={{ p: {xs: 2, sm: 3}, borderRadius: 3, height: 'fit-content', flex: '1', maxWidth: '400px'}}>
                                    <Stack spacing={2} >
                                        <h3 className="font-bold">Order Summary</h3>
                                        <div className="flex justify-between gap-3">
                                            <h3 className="text-(--outline-color)">Subtotal</h3>
                                            <h3 className="font-bold">₦ {subtotal}</h3>
                                        </div>
                                        <div className="flex justify-between gap-3n">
                                            <h3 className="text-(--outline-color)">Discount</h3>
                                            <h3 className="font-bold">₦0</h3>
                                        </div>
                                        <div className="flex justify-between gap-3">
                                            <h3 className="text-(--outline-color)">Delivery</h3>
                                            <h3 className="font-bold">₦0</h3>
                                        </div>
                                        <hr className="text-(--outline-color)" />
                                        <div className="flex justify-between gap-3">
                                            <h3 className="font-bold">Total</h3>
                                            <h3 className="font-bold">₦ {total}</h3>
                                        </div>

                                        <div className="h-10 sm:h-15 max-w-90 min-w-50 rounded-full overflow-hidden place-self-center">
                                            <PrimaryBtn text='Go to Checkout' />
                                        </div>
                                    </Stack>
                                </Paper>                                
                            </Stack>
                            <Button 
                                endIcon={<DeleteIcon />} 
                                variant="text" 
                                color="error" 
                                onClick={(e) => {
                                    dispatch(clearCart())
                                    setCartItems([])
                                }}
                                sx={{width: 150}}
                            >Clear Cart</Button>
                        </Stack>
                    </Paper>
                </Grid>
            </Container>
        </section>
        </>
    )
}

export default CartPage