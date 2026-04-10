import { Container, Divider, Grid, Paper, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { Link } from "react-router";
import { PrimaryBtn, SecondaryBtn } from "../components/Buttons";
import GoogleIcon from '@mui/icons-material/Google';
import kinahsFamilyLogo from '../assets/login_image.png'


export default function LoginPage(){
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    return (
        <>
        <section className='mb-10 mt-25 h-max md:h-[75vh]'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, maxWidth: 900, height: 'fit-content', marginInline: 'auto'}}>
                        <Stack spacing={3}>
                            <div>
                                <h2 className="font-bold mb-1.5">Welcome Back!</h2>
                                <p className="text-(--outline-color)">Please enter your login details below</p>
                            </div>
                            <Paper elevation={0} sx={{p: 3, borderRadius: 3}} >
                                <Stack direction='row' spacing={5} justifyContent='space-between'>
                                    <Stack spacing={3} flex='1'>
                                        <TextField
                                            label='Email'
                                            variant="outlined"
                                            placeholder="johndoe@example.com"
                                            value={email}
                                            onChange={(e)=> setEmail(e.target.value)}
                                        />

                                        <TextField
                                            label='Password'
                                            type="password"
                                            variant="outlined"
                                            value={password}
                                            onChange={(e)=> setPassword(e.target.value)}
                                        />

                                        <div className="text-right">
                                             <Link to='/auth/forget-password'>
                                                Forgot password?
                                            </Link>
                                        </div>
                                       

                                        <div className="h-15">
                                            <PrimaryBtn text='Login' />
                                        </div>
                                        
                                        <Divider> <span className="text-(--outline-color)">or</span> </Divider>

                                        <div className="h-15">
                                            <SecondaryBtn text='Login with google' StartIcon={GoogleIcon}/>
                                        </div>

                                        <p>Don't have an account? <span className="text-(--primary-color)"><Link to='/auth/register'>Register</Link></span></p>
                                        
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