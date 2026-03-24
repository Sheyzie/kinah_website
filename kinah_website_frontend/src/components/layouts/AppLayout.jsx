import { Outlet } from 'react-router-dom'
import Header from '../general/Header'
import Footer from '../general/Footer'


const AppLayout = () => {
    
    return (
        <>
            <Header />
            <Outlet />
            {/* <Footer /> */}
        </>
    )
}

export default AppLayout