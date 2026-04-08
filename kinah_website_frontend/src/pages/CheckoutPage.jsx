import { Accordion, AccordionDetails, AccordionSummary, Container, Grid, Paper, Typography, Alert, Box, TextField, Stack, FormControl, Autocomplete, MenuItem, CircularProgress, TableContainer, Table, TableHead, TableRow, TableCell, TableBody } from "@mui/material"
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useEffect, useMemo, useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import { DeliveryVendorAccordion, EmailAccordion, ShippingAddressAccordion } from "./CheckoutForm";
import { useSelector } from "react-redux";
import { createOrder, extractAddress, getDistanceKm } from "../helpers/orderHelper";
import { formatToCurrency } from "../utils/formatToCurrency";
import OrderPreviewModal from "../components/OrderPreviewModal";

{/* <Alert severity="success">This is a success Alert.</Alert>
<Alert severity="info">This is an info Alert.</Alert>
<Alert severity="warning">This is a warning Alert.</Alert>
<Alert severity="error">This is an error Alert.</Alert> */}

function CheckoutPage(){
    const currentUser = useSelector(state => state.user.user) || {}
    const products = useSelector(state => state.cart.items)

    const [email, setEmail] = useState(currentUser.email || "");
    const [emailError, setEmailError] = useState(false);
    const [shippingError, setShippingError] = useState(false);
    const [billingError, setBillingError] = useState(false);
    const [query, setQuery] = useState("");
    const [address, setAddress] = useState([]);
    const [shippingAddress, setShippingAddress] = useState(currentUser.shipping_address || {address_type: 'shipping'});
    const [billingAddress, setBillingAddress] = useState(currentUser.shipping_address || {address_type: 'billing'});
    const [vendor, setVendor] = useState(null)
    const [coupon, setCoupon] = useState('')
    const [shippingDistance, setShippingDistance] = useState(0)
    
    // form submition state
    const [submitError, setSubmitError] = useState({})
    
    // Accordion state
    const [expanded, setExpanded] = useState("email");

    // order preview modal
    const [openModal, setOpenModal] = useState(false);
    const [orderData, setOrderData] = useState({})

    let debounceTimer;
    const headOffice = [7.3986, 9.0765];
    useEffect(() => {
        clearTimeout(debounceTimer);
        if (query.length < 3) return;

        debounceTimer = setTimeout(() => {
            fetchAddressData()
        }, 500)

    }, [query])

    async function fetchAddressData() {
        
        const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1`
        );

        const data = await res.json();
        setAddress(data);
    }

    const handleChange = (value, field, address_type='') => {
        setSubmitError({})

        if (field === 'email') {
            setEmail(value);
            // simple regex validation
            const isValid = /\S+@\S+\.\S+/.test(value);
            setEmailError(!isValid);
            return
        }

        if (['street_address', 'apartment_address', 'postal_code'].includes(field)) {
            setShippingError(false)
            if (address_type === 'shipping') {
                setShippingError(false)
                setShippingAddress(prevAddress => ({...prevAddress, [field]: value}));
            
                if(!value) setShippingError(true);

            } else {
                setBillingError(false)
                setBillingAddress(prevAddress => ({...prevAddress, [field]: value}));
            
                if(!value) setBillingError(true);
            }
            
        }

        
    };

    const handleSearch = (value) => {
        setQuery(value);
    };

    const handleSelect = (place, address_type) => {
        const parsed = extractAddress(place);
        setQuery(place.display_name);
        setAddress([]);
        if(address_type === 'shipping') {
            setShippingAddress(prevAddress => ({...prevAddress, ...parsed}))
        } else if (address_type === 'billing') {
            setBillingAddress(prevAddress => ({...prevAddress, ...parsed}))
        }
        
    };

    const handleSubmit = async (e) => {
        setSubmitError({})

        if (!email || emailError) {
            setSubmitError({error: true, message: 'A valid email is required'})
            setExpanded('email')
            return
        }

        if (shippingError || !shippingAddress.city || !shippingAddress.state || !shippingAddress.country || !shippingAddress.street_address || !shippingAddress.apartment_address) {
            setSubmitError({error: true, message: 'A valid shipping address information is required'})
            setExpanded('shipping')
            return
        }

        if (billingError || !billingAddress.city || !billingAddress.state || !billingAddress.country || !billingAddress.street_address || !billingAddress.apartment_address) {
            setSubmitError({error: true, message: 'A valid billing address information is required'})
            setExpanded('billing')
            return
        }

        if (!vendor) {
            setSubmitError({error: true, message: 'Please select a valid delivery vendor'})
            setExpanded('delivery')
            return
        }

        const { kilometers, deliveryDate } = await getDistanceKm(headOffice, [shippingAddress.longitude, shippingAddress.latitude])

        setShippingDistance(kilometers || 0)

        const data = {
            customer_email: email,
            shipping_address: shippingAddress,
            billing_address: billingAddress,
            shipping_carrier: vendor.id,
            shipping_distance: kilometers || 0,
            estimated_delivery: deliveryDate,
            coupon_code: coupon,
            items: products.map(product => ({
                id: product.id, 
                product_name: product.name,
                product_category: product.category,
                product_type: product.type,
                package_type: product.package_type,
                quantity: product.quantity,
                unit_price: product.price,
                product_image: product.image
            }))
        }

        setOrderData(data)
        setOpenModal(true)


        // try {
        //     const { success, message, order } = await createOrder(data)
        // }
        // catch (err) {
        //     console.error(err)
        // }
        // finally{
        //     setIsLoading(false)
        // }
        
    }

    const handleAccordionChange = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
    };

    const deliveryVendors = [
        {
            id: '1',
            company_name: 'Gokada',
            cost_per_km: 30
        },
        {
            id: '2',
            company_name: 'DHL',
            cost_per_km: 300
        },
        {
            id: '3',
            company_name: 'Fedex',
            cost_per_km: 300
        },
    ]

    return (
        <>
        <section className='mb-10 mt-25'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content', marginBottom: 10}}>
                        <Box
                            component='form'
                            noValidate
                            autoComplete="off"
                        >
                            <Stack spacing={3}>
                                <EmailAccordion 
                                    email={email} 
                                    emailError={emailError} 
                                    handleChange={handleChange}
                                    expanded={expanded}
                                    handleAccordionChange={handleAccordionChange} 
                                />

                                <ShippingAddressAccordion 
                                    addresses={address}
                                    addressData={shippingAddress}
                                    setError={setShippingError}
                                    handleChange={handleChange}
                                    handleSelect={handleSelect}
                                    handleSearch={handleSearch}
                                    type='shipping'
                                    expanded={expanded}
                                    handleAccordionChange={handleAccordionChange}
                                />

                                <ShippingAddressAccordion 
                                    addresses={address}
                                    addressData={billingAddress}
                                    setError={setBillingError}
                                    handleChange={handleChange}
                                    handleSelect={handleSelect}
                                    handleSearch={handleSearch}
                                    type='billing'
                                    expanded={expanded}
                                    handleAccordionChange={handleAccordionChange}
                                />

                                <DeliveryVendorAccordion 
                                    vendors={deliveryVendors} 
                                    setVendor={setVendor}
                                    setError={setSubmitError}
                                    expanded={expanded}
                                    handleAccordionChange={handleAccordionChange}
                                />

                                <TextField
                                    label="Enter Coupon Code"
                                    variant="outlined"
                                    fullWidth
                                    value={coupon}
                                    onChange={(e) => setCoupon(e.target.value)}
                                />

                                {submitError.error? <Alert severity="error">{submitError.message}</Alert> : ''}

                                <div className="h-15">
                                    <PrimaryBtn text='Show Order Preview' action={handleSubmit} />
                                </div>
                                
                            </Stack>
                        </Box>
                    </Paper>

                    {/* <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content', marginBottom: 10}}>
                        <Stack spacing={2}>
                            <h3 className="font-bold">Order Summary</h3>
                            <div className="">
                                <h4>Shipping Information:</h4>
                                <address>No 19, CMD Road, Kosofe, Lagos, Nigeria</address>
                                
                            </div>
                            <div className="">
                                <h4>Delivery Information:</h4>
                                <p>Distance: <span>{shippingDistance || 0}</span> KM</p>
                                <p>Cost per KM: {formatToCurrency(vendor.cost_per_km || 0)}</p>
                                <p>Delivery Date : 06/04/2026</p>
                            </div>

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
                                        {products.map((product) => (
                                            <TableRow key={product.id}>
                                                <TableCell>
                                                    <div className="flex gap-3">
                                                        <img className="h-5" src={product.image} alt="" />
                                                        {product.name}
                                                    </div>
                                                </TableCell>
                                                <TableCell align="right">{product.quantity}</TableCell>
                                                <TableCell align="right">{formatToCurrency(product.price)}</TableCell>
                                                <TableCell align="right">{formatToCurrency(product.price * product.quantity)}</TableCell>
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
                                            <TableCell align="right">{formatToCurrency((shippingDistance * vendor.cost_per_km) || 0)}</TableCell>
                                        </TableRow>
                                        <TableRow>
                                            <TableCell colSpan={2}>Total</TableCell>
                                            <TableCell align="right">{formatToCurrency(total())}</TableCell>
                                        </TableRow>
                                    </TableBody>
                                </Table>
                            </TableContainer>

                            <Box sx={{ m: 1, position: 'relative' }} >
                                    <div className="h-15">
                                        <PrimaryBtn text='Create Order' action={handleSubmit} disabled={isloading} />
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
                    </Paper> */}

                    <OrderPreviewModal 
                        orderData={orderData}
                        openModal={openModal}
                        setOpenModal={setOpenModal}
                        vendor={vendor}
                    />


                </Grid>
            </Container>
        </section>
        </>
    )
}

export default CheckoutPage