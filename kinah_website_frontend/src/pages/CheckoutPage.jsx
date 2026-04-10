import { Container, Grid, Paper, Alert, Box, TextField, Stack } from "@mui/material"
import { useEffect, useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import { DeliveryVendorAccordion, EmailAccordion, ShippingAddressAccordion } from "./CheckoutForm";
import { useSelector } from "react-redux";
import { extractAddress, getDistanceKm, getVendors } from "../helpers/orderHelper";
import OrderPreviewModal from "../components/OrderPreviewModal";


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
    const [vendors, setVendors] = useState([])
    const [vendor, setVendor] = useState(null)
    const [coupon, setCoupon] = useState('')
    const [comment, setComment] = useState('')
    
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

        return () => {
            clearTimeout(debounceTimer);
        }

    }, [query])

    useEffect(() => {
        fetchVendors()

    }, [])

    async function fetchAddressData() {
        
        const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1`
        );

        const data = await res.json();
        setAddress(data);
    }

    async function fetchVendors() {
        const vendorList = await getVendors()
        setVendors(vendorList)
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

        const data = {
            customer_email: email,
            shipping_address: shippingAddress,
            billing_address: billingAddress,
            shipping_carrier: vendor.id,
            shipping_distance: kilometers || 0,
            estimated_delivery: deliveryDate,
            coupon_code: coupon,
            customer_note: comment,
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
        
    }

    const handleAccordionChange = (panel) => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
    };

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
                                    vendors={vendors} 
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

                                <TextField
                                    multiline
                                    label="Comment"
                                    variant="outlined"
                                    fullWidth
                                    value={comment}
                                    onChange={(e) => setComment(e.target.value)}
                                />

                                {submitError.error? <Alert severity="error">{submitError.message}</Alert> : ''}

                                <div className="h-15">
                                    <PrimaryBtn text='Show Order Preview' action={handleSubmit} />
                                </div>
                                
                            </Stack>
                        </Box>
                    </Paper>

                    <OrderPreviewModal 
                        orderData={orderData}
                        openModal={openModal}
                        setOpenModal={setOpenModal}
                        vendor={vendor}
                        setError={setSubmitError}
                    />


                </Grid>
            </Container>
        </section>
        </>
    )
}

export default CheckoutPage