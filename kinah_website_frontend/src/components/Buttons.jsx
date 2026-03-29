import { Button, Stack, IconButton, styled } from "@mui/material";
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import Avatar from '@mui/material/Avatar';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCartOutlined';
import Badge, { badgeClasses } from '@mui/material/Badge';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import { useSelector } from "react-redux";

export function PrimaryBtn({ text, action }) {
    return (
        <Button 
            variant="contained"
            onClick={action}
            sx={{
                backgroundColor: 'var(--primary-color)',
                '&:hover': {
                backgroundColor: 'var(--primary-color)', // optional: keep same on hover
                },
                height: '100%',
                width: '100%',
                mx: '10px',
            }}
        >{text}</Button>
    )
}

export function LoginProfileBtn({ isLoggedIn, showName }) {
    const user = useSelector((state) => state.user.user)
    return (
        <Stack 
            direction="row" 
            spacing={2} 
            sx={{
                cursor: 'pointer',
                alignItems: 'center',
                '& .arrow': {
                    transition: 'transform 0.2s ease',
                },
                '&:hover .arrow': {
                    transform: 'translateX(5px)',
                },
            }}>
            {isLoggedIn ? (
                <>
                <Avatar sx={{ bgcolor: 'var(--primary-color)' }}>{user.first_name[0]}{user.last_name[0]}</Avatar>
                {showName ? <h3>{user.first_name} {user.last_name}</h3> : ''}
                </>
            ) : (
                <>
                <PersonOutlineOutlinedIcon />
                    <h3>Login</h3>
                <KeyboardArrowDownIcon className="arrow" />
                </>
            )}                      
            
        </Stack>
    )
}

const CartBadge = styled(Badge)`
  & .${badgeClasses.badge} {
    top: -12px;
    right: -6px;
  }
`;


export function CartIconBtn() {
    const quantity = useSelector(state => state.cart.items.length)

    return (
        <IconButton
            sx={{
                color: 'black',
                borderColor: 'black',
                '&:hover': {
                borderColor: 'black',
                backgroundColor: 'rgba(0,0,0,0.04)', // subtle hover
                },
            }}
            >
            <ShoppingCartIcon fontSize="small" />
            <CartBadge 
                badgeContent={quantity + 1} 
                overlap="circular" 
                sx={{
                    '& .MuiBadge-badge' : {
                        backgroundColor: 'var(--primary-color)',
                        color: 'white'
                    }
                }}
            />
        </IconButton>
    )
}

