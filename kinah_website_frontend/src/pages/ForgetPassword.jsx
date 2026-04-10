import { Container, Grid, Paper, TextField } from "@mui/material";
import { useState } from "react";
import { PrimaryBtn } from "../components/Buttons";
import { useNavigate } from "react-router";

export default function ForgotPassword(){
    const [email, setEmail] = useState('')
    const navigate = useNavigate()

    const handleClick = (e) => {
        // get response from backend
        navigate('/accounts/set-password/uid/token')
    }
    return (
        <>
        <section className='h-screen'>
            <Container maxWidth="xl" sx={{height: '100%'}}>
                <Grid container width='100%' height='100%' alignItems='center'>
                    <Paper elevation={3} sx={{ p: 3, borderRadius: 3, maxWidth: 700, height: 'fit-content', marginInline: 'auto'}}>
                        <h2 className="font-bold">Forget Password</h2>
                        <p className="text-(--outline-color) mb-5">Enter your email address below</p>
                        <TextField
                            fullWidth
                            label='Email'
                            variant="outlined"
                            placeholder="johndoe@example.com"
                            value={email}
                            onChange={(e)=> setEmail(e.target.value)}
                        />
                        <div className="h-15 my-5">
                            <PrimaryBtn text='Continue' action={handleClick}/>
                        </div>
                    </Paper>
                </Grid>
            </Container>
        </section>
        </>
    )
}