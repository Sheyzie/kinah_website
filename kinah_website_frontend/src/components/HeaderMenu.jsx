import { useState } from 'react';
import {
  Stack,
  IconButton,
  Drawer,
  Box,
  styled
} from '@mui/material';
import Badge, { badgeClasses } from '@mui/material/Badge';
import MenuIcon from '@mui/icons-material/Menu';
import CloseIcon from '@mui/icons-material/Close';
import { LoginProfileBtn, CartIconBtn } from './Buttons';
import PersonOutlineOutlinedIcon from '@mui/icons-material/PersonOutlineOutlined';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import ShoppingCartIcon from '@mui/icons-material/ShoppingCart';
import Avatar from '@mui/material/Avatar';
import { useNavigate } from 'react-router';


const CartBadge = styled(Badge)`
  & .${badgeClasses.badge} {
    top: -12px;
    right: -6px;
  }
`;


function HeaderMenu({ isLoggedIn }) {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate()

  return (
    <>
      {/* 🔹 Hamburger Button */}
      <IconButton onClick={() => setOpen(true)}>
        {open ? <CloseIcon /> : <MenuIcon />}
      </IconButton>

      {/* 🔹 Drawer Menu */}
      <Drawer
        anchor="right"
        open={open}
        onClose={() => setOpen(false)}
        sx={{
            '& .MuiDrawer-paper': {
            height: 230, 
            borderRadius: '50px 0 0 50px',
            opacity: 0.9,
            },
        }}
      >
        <Box sx={{ width: 250, p: 2 }}>
          
          {/* Close button */}
          <IconButton onClick={() => setOpen(false)}>
            {open ? <CloseIcon /> : <MenuIcon />}
          </IconButton>

          <br />
          <br />

          {/* 🔹 Login Section */}
          <LoginProfileBtn isLoggedIn={isLoggedIn} showName={true} />
          <br />

          {/* 🔹 Cart Section */}
          <Stack direction='row' spacing={2} alignItems='center' onClick={()=> navigate('cart')}>
            <CartIconBtn quantity={3} />
            <h3 onClick={()=> navigate('cart')}>Cart</h3>
          </Stack>

        </Box>
      </Drawer>
    </>
  );
}

export default HeaderMenu;