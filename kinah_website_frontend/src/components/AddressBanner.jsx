import { Autocomplete, Paper, Stack, TextField } from "@mui/material"
import { PrimaryBtn } from "../components/Buttons";
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import { useEffect, useState } from "react";
import { extractAddress } from "../helpers/orderHelper";

export default function AddressBanner({ addressData }){
    const [editMode, setEditMode] = useState(false)
    const [address, setAddress] = useState(addressData)
    const [fetchedAddress, setFetchedAddress] = useState([])
    const [query, setQuery] = useState("");

    let debounceTimer

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

    async function fetchAddressData() {
        
        const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${query}&addressdetails=1`
        );

        const data = await res.json();
        setFetchedAddress(data);
    }

    const handleEdit = (e) => {
        setEditMode(true)
        console.log('Handled')
    }

    const handleSave = (e) => {
        console.log('Handled')
        setEditMode(false)
    }

    const handleSearch = (value) => {
        setQuery(value);
    };

    const handleSelect = (place) => {
        const parsed = extractAddress(place);
        console.log(parsed)
        setQuery(place.display_name);
        setFetchedAddress([]);
        setAddress(prevAddress => ({...prevAddress, ...parsed}))        
    };

    return (
        <>
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack spacing={3}>
                <div className="flex justify-between">
                    <h2 className="font-bold">{address.address_type === 'shipping'? 'Shipping' : 'Billing'} Information</h2>

                    <div className="w-25">
                        {editMode ? 
                            <PrimaryBtn text='Save' EndIcon={SaveIcon} action={handleSave} />:
                            <PrimaryBtn text='Edit' EndIcon={EditIcon} action={handleEdit} />
                        }
                    </div>
                </div>
                <hr className="opacity-45" />

                <Stack spacing={3} direction={{xs: 'column', sm: 'column', md: 'row'}} justifyContent='space-between'>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">CITY</h3>
                        {editMode ? 
                            <Autocomplete
                                id="country-select-demo"
                                sx={{ maxWidth: 210, minWidth: {xs: 210, sm: 180} }}
                                options={fetchedAddress || []}
                                autoHighlight
                                getOptionLabel={(option) => option.display_name || ""}

                                onChange={(event, value) => {
                                    if (value) {
                                        handleSelect(value); 
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
                                    margin="none"
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
                            /> :
                            // <TextField variant="outlined" value={address.city} onChange={(e) => setAddress(prevAddress => ({...prevAddress, city: e.target.value}))} /> : 
                            <h3 className="text-2xl">{address.city}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">STATE</h3>
                        {editMode ? 
                            <TextField disabled variant="outlined" value={address.state} onChange={(e) => setAddress(prevAddress => ({...prevAddress, state: e.target.value}))} /> : 
                            <h3 className="text-xl">{address.state}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">COUNTRY</h3>
                        {editMode ? 
                            <TextField disabled variant="outlined" value={address.country} onChange={(e) => setAddress(prevAddress => ({...prevAddress, country: e.target.value}))} /> : 
                            <h3 className="text-xl">{address.country}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">APARTMENT</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={address.apartment_address} onChange={(e) => setAddress(prevAddress => ({...prevAddress, apartment_address: e.target.value}))} /> : 
                            <h3 className="text-xl">{address.apartment_address}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">STREET</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={address.street_address} onChange={(e) => setAddress(prevAddress => ({...prevAddress, street_address: e.target.value}))} /> : 
                            <h3 className="text-xl">{address.street_address}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">POSTAL CODE</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={address.postal_code || ''} onChange={(e) => setAddress(prevAddress => ({...prevAddress, postal_code: e.target.value}))} /> : 
                            <h3 className="text-xl">{address.postal_code}</h3>
                        }
                    </div>
                </Stack>
            </Stack>
        </Paper>
        </>
    )
}