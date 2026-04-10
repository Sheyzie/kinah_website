import { Paper, Box, Stack, CircularProgress, TableContainer, Table, TableHead, TableRow, TableCell, TableBody, Modal } from "@mui/material"
import { useEffect, useMemo, useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import { useSelector } from "react-redux";
import { processOrder, extractAddress, formatDeliveryDate, getDistanceKm } from "../helpers/orderHelper";
import { formatToCurrency } from "../utils/formatToCurrency";
// import { usePaystackPayment } from 'react-paystack';


export default function OrderPreviewModal({ orderData, vendor, openModal, setOpenModal, setError }) {
    const [submitError, setSubmitError] = useState({})
    const [isloading, setIsLoading] = useState(false)

    const subtotal = () => {
        return orderData.items?.reduce((st, product) => st + (product.quantity * product.unit_price), 0)
    }

    const discount = () => {
        // get coupon discount
        return {discount_type: 'percent', discount_value: 5}
    }

    const calculate_vat = () => {
        const vat_percent = 7.5
        return (subtotal() - discount().discount_value) * (vat_percent / 100)
    }

    const total = () => {
        return (subtotal() - discount().discount_value) + calculate_vat() + ((orderData.shipping_distance * vendor?.cost_per_km) || 0)
    }

    const onPaymentSuccess = async (response) => {
        // Step 1: send to backend
        const res = await fetch("/verify/", {
            method: "POST",
            body: JSON.stringify({
            reference: response.reference
            })
        });

        // Step 2: backend confirms
        const data = await res.json();

        if (data.status === "success") {
            // show success UI
        } else {
            // show error (fake or failed payment)
        }
    };

    const onPaymentClose = () => {
        // maybe show message or allow retry
        setIsLoading(false)
    }

    const handlePaymentProcess = async (e) => {
        setIsLoading(true)
        const result = await processOrder(orderData)
        if (!result.success) {
            setIsLoading(false)
            setOpenModal(false)
            setError({error: true, message: result.message})
        }

        const order = result.order

        const config = {
            ref: order.order_number,
            email: "user@email.com",
            amount: 50,
            currency: "NGN",
            key: import.meta.env.VITE_PAYSTACK_PUBLIC_KEY,
        };

        const payWithPaystack = () => {
            const handler = window.PaystackPop.setup({
                ...config,

                callback: function (response) {
                    // handle payment success
                    console.log(response.message)
                    onPaymentSuccess()
                },

                onClose: function () {
                    onPaymentClose()
                },
            });

            handler.openIframe();
        };

        try{
            payWithPaystack()
        } catch (err) {
            console.log('----- ??? -----')
        }

    }

    const style = {
        position: 'relative',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -30%)',
        bgcolor: 'background.paper',
        maxWidth: 900,
        p: 3, borderRadius: 3,
        marginBottom: 10
    };

    return (
        <Modal
            open={openModal}
            onClose={()=> setOpenModal(false)}
            aria-labelledby="modal-modal-title"
            aria-describedby="modal-modal-description"
            sx={{overflowY: 'scroll', paddingLeft: 3, paddingRight: 3, paddingTop: 20}}
        >
            {/* <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content', marginBottom: 10}}> */}
            <Paper elevation={3} sx={style}>
                <Stack spacing={5}>
                    <h3 className="font-bold">Order Preview</h3>

                    <TableContainer component={Paper}>
                        <Table sx={{ minWidth: 700 }} aria-label="spanning table">
                            <TableHead>
                                <TableRow>
                                    <TableCell align="center" colSpan={4}>
                                        Products
                                    </TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell>Name</TableCell>
                                    <TableCell align="right">Qty.</TableCell>
                                    <TableCell align="right">Unit Price</TableCell>
                                    <TableCell align="right">Total</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {orderData.items?.map((product) => (
                                    <TableRow key={product.id}>
                                        <TableCell>
                                            <div className="flex gap-3">
                                                <img className="h-5" src={product.product_image} alt="" />
                                                {product.product_name}
                                            </div>
                                        </TableCell>
                                        <TableCell align="right">{product.quantity}</TableCell>
                                        <TableCell align="right">{formatToCurrency(product.unit_price)}</TableCell>
                                        <TableCell align="right">{formatToCurrency(product.unit_price * product.quantity)}</TableCell>
                                    </TableRow>
                                ))}
                                <TableRow>
                                    <TableCell rowSpan={5} />
                                    <TableCell colSpan={2}>Subtotal</TableCell>
                                    <TableCell align="right">{formatToCurrency(subtotal())}</TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell>Discount</TableCell>
                                    <TableCell align="right">{(
                                        discount().discount_type === 'percent' ? 
                                        `${discount().discount_value}%` : 
                                        formatToCurrency(discount().discount_value))}</TableCell>
                                    <TableCell align="right">{formatToCurrency(discount().discount_value)}</TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell>vat</TableCell>
                                    <TableCell align="right">{'7.5%'}</TableCell>
                                    <TableCell align="right">{formatToCurrency(calculate_vat())}</TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell colSpan={2}>Delivery</TableCell>
                                    <TableCell align="right">{formatToCurrency((orderData.shipping_distance * vendor?.cost_per_km) || 0)}</TableCell>
                                </TableRow>
                                <TableRow>
                                    <TableCell sx={{fontWeight: 700}} colSpan={2}>Total</TableCell>
                                    <TableCell align="right" sx={{fontWeight: 700}} >{formatToCurrency(total())}</TableCell>
                                </TableRow>
                            </TableBody>
                        </Table>
                    </TableContainer>

                    <div className="flex gap-5 sm:gap-15 flex-col sm:flex-row justify-center">
                        <div>
                            <h4 className="text-(--outline-color)">Customer</h4>
                            <p>{orderData.customer_email}</p>
                        </div>
                        <div>
                            <h4 className="text-(--outline-color)">Shipping Address</h4>
                            <address className="">
                                {orderData?.shipping_address?.apartment_address}, {orderData?.shipping_address?.street_address},
                            </address>
                            <address>
                                {orderData?.shipping_address?.city}, {orderData?.shipping_address?.state} State, {orderData?.shipping_address?.country}
                            </address>
                        </div>

                        <div>
                            <h4 className="text-(--outline-color)">Delivery</h4>
                            <h4 className="font-bold">Delivered at {formatDeliveryDate(new Date(orderData.estimated_delivery))}</h4>
                        </div>
                    </div>

                    <div className="flex justify-between flex-col sm:flex-row gap-5 sm:gap-0">
                        <p className="italics">{vendor?.company_name} charges <span className="">{formatToCurrency(vendor?.cost_per_km || 0)}</span> per kilometer</p>
                        <p className="text-(--outline-color)"><span className="text-3xl text-black font-bold">{orderData.shipping_distance || 0}</span> KM away</p>
                    </div>

                    

                    <Box sx={{ m: 1, position: 'relative' }} >
                            <div className="h-15">
                                <PrimaryBtn text='Make Payment' action={handlePaymentProcess} disabled={isloading} />
                            </div>

                            {isloading && (
                                <CircularProgress
                                    size={24}
                                    sx={{
                                    color: 'inherit',
                                    position: 'absolute',
                                    top: '50%',
                                    left: '50%',
                                    marginTop: '-12px',
                                    marginLeft: '-12px',
                                    }}
                                />
                            )}

                        </Box>
                </Stack>
            </Paper>
            
        </Modal>
    )
}