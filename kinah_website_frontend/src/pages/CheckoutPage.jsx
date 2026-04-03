import { Accordion, AccordionDetails, AccordionSummary, Container, Grid, Paper, Typography, Alert, Box, TextField, Stack, FormControl, Autocomplete, MenuItem, CircularProgress } from "@mui/material"
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useEffect, useMemo, useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import { DeliveryVendorAccordion, EmailAccordion, ShippingAddressAccordion } from "./CheckoutForm";

{/* <Alert severity="success">This is a success Alert.</Alert>
<Alert severity="info">This is an info Alert.</Alert>
<Alert severity="warning">This is a warning Alert.</Alert>
<Alert severity="error">This is an error Alert.</Alert> */}

function CheckoutPage(){
    const [email, setEmail] = useState("");
    const [emailError, setEmailError] = useState(false);
    const [shippingError, setShippingError] = useState(false);
    const [billingError, setBillingError] = useState(false);
    const [query, setQuery] = useState("");
    const [address, setAddress] = useState([]);
    const [shippingAddress, setShippingAddress] = useState({address_type: 'shipping'});
    const [billingAddress, setBillingAddress] = useState({address_type: 'billing'});
    const [vendor, setVendor] = useState('')
    const [coupon, setCoupon] = useState('')
    const [submitError, setSubmitError] = useState({})
    const [isloading, setIsLoading] = useState(false)

    let debounceTimer;

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

    const extractAddress = (place) => {
        const addressData = place.address
        const formatedAddress = {
            place_id: place.place_id,
            country: addressData.country,
            city: addressData.city || addressData.county,
            state: addressData.state.replace(/state/gi, "").trim(),
            display_name: place.display_name,
            longitude: place.lon,
            latitutde: place.lat
        }

        return formatedAddress
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

    const handleSubmit = (e) => {
        if (isloading) return;

        if (!email || emailError) {
            setSubmitError({error: true, message: 'A valid email is required'})
            return
        }

        if (shippingError || !shippingAddress.city || !shippingAddress.state || !shippingAddress.country || !shippingAddress.street_address || !shippingAddress.apartment_address) {
            setSubmitError({error: true, message: 'A valid shipping address information is required'})
            return
        }

        if (billingError || !billingAddress.city || !billingAddress.state || !billingAddress.country || !billingAddress.street_address || !billingAddress.apartment_address) {
            setSubmitError({error: true, message: 'A valid billing address information is required'})
            return
        }

        if (!vendor) {
            setSubmitError({error: true, message: 'Please select a valid delivery vendor'})
            return
        }

        setIsLoading(true)
        setIsLoading(true)

        const data = {
            customer_email: email,
            shipping_address: shippingAddress,
            billing_address: billingAddress,
            shipping_carrier: vendor,
            coupon_code: coupon
        }

        console.log(data)
        // process order creation
        
    }

    const deliveryVendors = [
        {
            id: '1',
            company_name: 'Gokada'
        },
        {
            id: '2',
            company_name: 'DHL'
        },
        {
            id: '3',
            company_name: 'Fedex'
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
                                <EmailAccordion email={email} emailError={emailError} handleChange={handleChange} />

                                <ShippingAddressAccordion 
                                    addresses={address}
                                    addressData={shippingAddress}
                                    setError={setShippingError}
                                    handleChange={handleChange}
                                    handleSelect={handleSelect}
                                    handleSearch={handleSearch}
                                    type='shipping'
                                />

                                <ShippingAddressAccordion 
                                    addresses={address}
                                    addressData={billingAddress}
                                    setError={setBillingError}
                                    handleChange={handleChange}
                                    handleSelect={handleSelect}
                                    handleSearch={handleSearch}
                                    type='billing'
                                />

                                <DeliveryVendorAccordion vendors={deliveryVendors} setVendor={setVendor} />

                                <TextField
                                    label="Enter Coupon Code"
                                    variant="outlined"
                                    fullWidth
                                    value={coupon}
                                    onChange={(e) => setCoupon(e.target.value)}
                                />

                                {submitError.error? <Alert severity="error">{submitError.message}</Alert> : ''}

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
                        </Box>
                    </Paper>
                </Grid>
            </Container>
        </section>
        </>
    )
}

export default CheckoutPage