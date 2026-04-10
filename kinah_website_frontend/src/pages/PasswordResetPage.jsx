import { Container, Divider, Grid, Paper, Stack, TextField } from "@mui/material";
import { useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import kinahsFamilyLogo from '../assets/login_image.png'
import { useNavigate, useParams } from "react-router";

export default function PasswordResetPage(){
    const [userData, setUserData] = useState({})
    const { uid, token } = useParams()
    const navigate = useNavigate()
    console.log(uid, token)

    const handleClick = () => {
        // send new password, uid, token to backend
        navigate('/auth/login')
    }

    return (
        <>
        <section className='h-screen'>
            <Container maxWidth="xl" sx={{height: '100%'}}>
                <Grid container size={{ xs: 12, sm: 6 , md: 9}} width='100%' height='100%' alignItems='center'>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, maxWidth: 900, height: 'fit-content', marginInline: 'auto'}}>
                        <Stack spacing={3}>
                            <div>
                                <h2 className="font-bold mb-1.5">Reset Password</h2>
                                <p className="text-(--outline-color)">Please enter new password below</p>
                            </div>
                            <Paper elevation={0} sx={{p: 3, borderRadius: 3}} >
                                <Stack direction='row' spacing={5} justifyContent='space-between'>
                                    <Stack spacing={3} flex='1'>

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

                                        <div className="h-15">
                                            <PrimaryBtn text='Reset Password' action={handleClick}/>
                                        </div>
                                        
                                    </Stack>
                                    <div className="w-70 hidden md:block">
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