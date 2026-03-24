import { Stack, Container, Button } from '@mui/material';
import { Link, useNavigate } from 'react-router';
import logo from '../../assets/logo_full.png'
import devLogo2 from '../../assets/bshp_logo_white.png'
import KeyboardDoubleArrowUpIcon from '@mui/icons-material/KeyboardDoubleArrowUp';
import XIcon from '@mui/icons-material/X';
import LinkedInIcon from '@mui/icons-material/LinkedIn';
import InstagramIcon from '@mui/icons-material/Instagram';
import FacebookIcon from '@mui/icons-material/Facebook';

export default function Footer(){
    const navigate = useNavigate()

    return (
        <footer className="w-full py-6 bg-(--secondary-color) text-white">
            <Container maxWidth='xl'>
                <Stack direction={{ xs: 'column', sm: 'row' }} spacing={{xs:5, sm:15}}>
                    <Stack direction='column' justifyContent={{xs: 'center', sm:'start'}}>
                        <div>
                            <img src={logo} alt="" />
                        </div>
                        <p>Dress well, Live well</p>
                    </Stack>
                    <Stack direction={{ sm: 'column', xs: 'row' }} spacing={1}>
                        <Link to='/'>Home</Link>
                        <Link to='/cart'>Cart</Link>
                        <Link to='/me'>Account</Link>
                        <Link to='/contact'>Contact Us</Link>
                    </Stack>
                    <Stack direction='column' spacing={2}>
                        <Stack direction='row' spacing={1}>
                            <Link to='/'>
                                <XIcon />
                            </Link>
                            <Link to='/'>
                                <LinkedInIcon />
                            </Link>
                            <Link to='/'>
                                <InstagramIcon />
                            </Link>
                            <Link to='/'>
                                <FacebookIcon />
                            </Link>
                        </Stack>

                        <Button 
                            variant='outlined'
                            startIcon={<KeyboardDoubleArrowUpIcon />}
                            onClick={()=> navigate('/')}
                            sx={{
                                borderColor: '#fff',
                                '&:hover': {
                                borderColor: '#fff', // optional: keep same on hover
                                },
                                color: '#fff',
                                height: '100%',
                            }}
                            >
                            Back to top
                        </Button>
                    </Stack>
                </Stack>
                <p className='text-sm opacity-65 justify-self-center mt-8'>Copyright &copy; 2024. Kinahs. All Rights Reserved</p>

                <p className='text-sm opacity-30 justify-self-end'>powered by <img className='h-8' src={devLogo2} alt="" /></p>
            </Container>
        </footer>
    )
}