import { useState } from 'react';
import { Box, TextField, createTheme, ThemeProvider } from '@mui/material';
import { PrimaryBtn } from './Buttons';

export default function SearchBox() {
    const [searchValue, setSearchValue] = useState()

    const handleChange = (e) => {
        setSearchValue(e.target.value)
    }

    const handleSearchBtnClick = (e) => {
        console.log(searchValue)
    }

    const theme = createTheme({
        palette: {
            background: {
                paper: 'var(--outline-color)',
            },
        }
    })

    return (
        <ThemeProvider theme={theme}>
            <Box
                component="form"
                sx={{ 
                    width: '800px',
                    display: 'flex',
                    height: '100%'
                    }}
                noValidate
                autoComplete="off"
                >
                <TextField 
                    id="search-bar" 
                    variant="outlined" 
                    onChange={handleChange}
                    placeholder="Search products and category"
                    sx={{
                        flex: '1',
                        height: '100%',
                        '& .MuiOutlinedInput-root': {
                            '& input': {
                                // height: '100%'
                            },
                            '& fieldset': {
                                borderColor: 'background.paper', // default border
                                height: '95%',
                            },
                            '&:hover fieldset': {
                                borderColor: 'background.paper', // on hover
                            },
                            '&.Mui-focused fieldset': {
                                borderColor: 'background.paper', // on focus
                            },
                            },
                            // '& .MuiInputBase-input': {
                            // color: 'background.paper', // text color
                            // },
                            '& .MuiInputBase-input::placeholder': {
                            color: 'background.paper',
                            opacity: 0.7,
                        },
                    }}
                    
                />

                <div className='mr-8 ml-2'>
                    <PrimaryBtn text='Search' action={handleSearchBtnClick}/>
                </div>
            </Box>
        </ThemeProvider>
    )
}