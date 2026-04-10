import { Container, Divider, Grid, Paper, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { Link } from "react-router";
import { PrimaryBtn, SecondaryBtn } from "../components/Buttons";
import GoogleIcon from '@mui/icons-material/Google';
import kinahsFamilyLogo from '../assets/login_image.png'

export default function RegisterPage(){
    const [userData, setUserData] = useState({})

    return (
        <>
        <section className='mb-10 mt-25 h-max md:h-[75vh]'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, maxWidth: 900, height: 'fit-content', marginInline: 'auto'}}>
                        <Stack spacing={3}>
                            <div>
                                <h2 className="font-bold mb-1.5">Join Our Registered Buyers</h2>
                                <p className="text-(--outline-color)">Please enter your details below</p>
                            </div>
                            <Paper elevation={0} sx={{p: 3, borderRadius: 3}} >
                                <Stack direction='row' spacing={5} justifyContent='space-between'>
                                    <Stack spacing={3} flex='1'>

                                        <div className="flex justify-between flex-col md:flex-row gap-5">
                                            <TextField
                                                label='First Name'
                                                variant="outlined"
                                                placeholder="John"
                                                value={userData.first_name || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, first_name: e.target.value}))}
                                            />
                                            <TextField
                                                label='Last Name'
                                                variant="outlined"
                                                placeholder="John"
                                                value={userData.last_name || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, last_name: e.target.value}))}
                                            />
                                        </div>

                                        <div className="flex justify-between gap-5 flex-col md:flex-row">
                                            <TextField
                                                label='Email'
                                                variant="outlined"
                                                placeholder="johndoe@example.com"
                                                value={userData.email || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, email: e.target.value}))}
                                            />
                                            <TextField
                                                label='Phone'
                                                variant="outlined"
                                                placeholder="+2348100000000"
                                                value={userData.phone || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, phone: e.target.value}))}
                                            />
                                        </div>

                                        <div className="flex justify-between gap-5 flex-col md:flex-row">
                                            <TextField
                                                label='Password'
                                                type="password"
                                                variant="outlined"
                                                value={userData.password || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, password: e.target.value}))}
                                            />

                                            <TextField
                                                label='Confirm Password'
                                                type="password"
                                                variant="outlined"
                                                value={userData.password || ''}
                                                onChange={(e)=> setUserData(prevData => ({...prevData, password: e.target.value}))}
                                            />
                                        </div>

                                        <div className="h-15">
                                            <PrimaryBtn text='Register' />
                                        </div>
                                        
                                        <Divider> <span className="text-(--outline-color)">or</span> </Divider>

                                        <div className="h-15">
                                            <SecondaryBtn text='Register with google' StartIcon={GoogleIcon}/>
                                        </div>

                                        <p>Already have an account? <span className="text-(--primary-color)"><Link to='/auth/login'>Log in</Link></span></p>
                                        
                                    </Stack>
                                    <div className="w-80 hidden md:block">
                                        <img className="h-full object-fill" src={kinahsFamilyLogo} alt="Kinahs logo" />
                                    </div>
                                </Stack>
                            </Paper>
                        </Stack>
                    </Paper>
                </Grid>
            </Container>
        </section>
        </>
    )
}