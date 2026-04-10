import { Accordion, AccordionDetails, AccordionSummary, Container, Grid, Paper, Typography, Alert, Box, TextField, Stack, FormControl, Autocomplete, MenuItem } from "@mui/material"
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { useState } from "react";
import { formatToCurrency } from "../utils/formatToCurrency";


export function EmailAccordion({email, emailError, handleChange, expanded, handleAccordionChange}) {
    return (
        <Accordion
            expanded={expanded === "email"}
            onChange={handleAccordionChange("email")}
        >
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1-content"
                id="panel1-header"
            >
                <Typography component="h2">Customer Info</Typography>
            </AccordionSummary>

            <AccordionDetails>
                <TextField 
                    required 
                    label="Email" 
                    placeholder="johndoe@example.com" 
                    variant="outlined" 
                    type="email" 
                    value={email}
                    onChange={(e) => handleChange(e.target.value, 'email')}
                    error={emailError}
                    helperText={emailError ? "Invalid email format" : ""}
                />
            </AccordionDetails>
        </Accordion>
    )
}

export function ShippingAddressAccordion ({ addresses, addressData, setError, handleChange, handleSelect, handleSearch, type, expanded, handleAccordionChange }) {
    const [streetAddressError, setStreetAddressError] = useState(false)
    const [apartmentAddressError, setApartmentAddressError] = useState(false)
    const [postalCodeError, setPostalCodeError] = useState(false)
    
    return (
        <Accordion
            expanded={expanded === type}
            onChange={handleAccordionChange(type)}
        >
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1-content"
                id="panel1-header"
            >
                <Typography component="h2">{type === 'shipping' ? 'Shipping' : 'Billing'} Address</Typography>
            </AccordionSummary>

            <AccordionDetails>
                <Autocomplete
                    id="country-select-demo"
                    // sx={{ width: 300 }}
                    options={addresses || []}
                    autoHighlight
                    getOptionLabel={(option) => option.display_name || ""}

                    onChange={(event, value) => {
                        if (value) {
                            handleSelect(value, type); 
                        }
                    }}
                    renderOption={(props, option) => (
                        <li {...props} key={option.place_id}>
                        {option.display_name}
                        </li>
                    )}

                    renderInput={(params) => (
                        <TextField
                        {...params}
                        label="Search City or County"
                        placeholder="kosofe, ikeja, oshodi"
                        margin="normal"
                        onChange={(e) => handleSearch(e.target.value)}
                        slotProps={{
                            htmlInput: {
                                ...params.inputProps,
                                autoComplete: 'new-password', // disable autocomplete and autofill
                                // type: 'search',
                            },
                        }}
                        />
                    )}
                />

                <TextField 
                    required 
                    fullWidth
                    label="Street Address" 
                    placeholder="St Peter street" 
                    variant="outlined" 
                    margin="normal"
                    value={addressData.street_address || ''}
                    onChange={(e) => {
                        handleChange(e.target.value, 'street_address', type)
                        if (!addressData.street_address) {
                            setStreetAddressError(true)
                            setError(true)
                        } else {
                            setStreetAddressError(false)
                            setError(false)
                        }
                    }}
                    error={streetAddressError}
                    helperText={streetAddressError ? "Street address is required" : ""}
                />

                <TextField 
                    required 
                    fullWidth
                    label="Appartment Address" 
                    placeholder="No. 5, Block 5" 
                    variant="outlined" 
                    margin="normal"
                    value={addressData.apartment_address || ''}
                    onChange={(e) => {
                        handleChange(e.target.value, 'apartment_address', type)
                        if (!addressData.apartment_address) {
                            setApartmentAddressError(true)
                            setError(true)
                        } else {
                            setApartmentAddressError(false)
                            setError(false)
                        }
                    }}
                    error={apartmentAddressError}
                    helperText={apartmentAddressError ? "Appartment address is required" : ""}
                />

                <TextField 
                    fullWidth
                    label="Postal Code" 
                    placeholder="000000" 
                    variant="outlined" 
                    margin="normal"
                    value={addressData.postal_code || ''}
                    onChange={(e) => {
                        const currentValue = e.target.value
                        handleChange(currentValue, 'postal_code', type)
                        if (!currentValue || isNaN(currentValue) || currentValue.length !== 6) {
                            setPostalCodeError(true)
                            setError(true)
                        } else {
                            setPostalCodeError(false)
                            setError(false)
                        }
                    }}
                    error={postalCodeError}
                    helperText={postalCodeError ? "Postal code must be number of 6 digits" : ""}
                />
            </AccordionDetails>
        </Accordion>
    )
}

export function DeliveryVendorAccordion ({ vendors, setVendor, expanded, handleAccordionChange, setError }) {

    return (
        <Accordion
            expanded={expanded === "delivery"}
            onChange={handleAccordionChange("delivery")}
        >
            <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                aria-controls="panel1-content"
                id="panel1-header"
            >
                <Typography component="h2">Delivery Vendor</Typography>
            </AccordionSummary>

            <AccordionDetails>
                <TextField
                    select
                    label="Select vendor"
                    variant="outlined"
                    fullWidth
                    defaultValue=''
                    onChange={(e) => {
                        setError({})
                        setVendor(vendors.find(vendor => vendor.id == e.target.value))
                    }}
                >
                    <MenuItem value=''></MenuItem>
                    {vendors.map(vendor => {
                        return <MenuItem key={vendor.id} value={vendor.id}>{vendor.company_name} - {formatToCurrency(vendor.cost_per_km)}</MenuItem>
                    })}
                    
                </TextField>
            </AccordionDetails>
        </Accordion>
    )
}