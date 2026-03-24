import logo_full from '../../assets/logo_full.png'
import logo_family from '../../assets/kinahs_logo_family.png'
import { Stack, Container } from '@mui/material';
import HeaderMenu from '../HeaderMenu';
import SearchBox from '../SearchBox';
import { LoginProfileBtn, CartIconBtn } from '../Buttons'


function Header() {
    const isLoggedIn = true

    return (
        <>
        <header className="absolute top-0 bg-white h-15.5 w-screen py-2 flex align-middle">
            <Container maxWidth='xl'>
                <div className="flex flex-1 justify-between my-auto h-full">
                    <div className="flex-1 flex gap-10 align-middle sm:max-w-5xl min-w-10 h-full">
                        <div className="w-50 sm:w-30 overflow-hidden">
                            <picture className='w-full h-full '>
                                <source media="(max-width: 480px)" srcSet={logo_family} />
                                {/* <source media="(max-width: 768px)" srcSet={logo_family} /> */}
                                <img src={logo_full} className="w-full h-full object-contain" />
                            </picture>
                        </div>
                        <SearchBox />
                    </div>
                    <div className="sm:w-52.5 w-5 flex align-middle justify-end">
                        <Stack direction="row" spacing={3} alignItems='center' onClick={()=> console.log('It has it')}>
                            <div className='hidden sm:flex'>
                                <LoginProfileBtn isLoggedIn={isLoggedIn} />
                                <CartIconBtn quantity={3} />
                            </div>

                            <div className="sm:hidden">
                                {/* hamburger */}
                                <HeaderMenu  isLoggedIn={isLoggedIn} />
                            </div>
                            
                        </Stack>
                    </div>
                </div>
            </Container>
        </header>
        <div className='mt-15 w-full'></div>
        </>
    )
}

export default Header