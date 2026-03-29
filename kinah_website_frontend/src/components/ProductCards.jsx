import { useState } from 'react';
import {
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Button,
  TablePagination,
  Box,
  Stack
} from '@mui/material';
import productImage from '../assets/product_image.png'
import { PrimaryBtn } from './Buttons';
import { Link } from 'react-router';

const ProductCards = () => {
  const products = Array.from({ length: 50 }, (_, i) => i + 1);

  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(6);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0); // reset to first page
  };

  const paginatedProducts = products.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  const productData = {
    id: 1,
    product_name: 'Givenchy Up and Down',
    detail: 'Fitting top and knicker for male',
    price: 10000,
    image: productImage,
    quantity: 89,
    category: 'male'
  }

  return (
    
    <Box>
      <div className='p-10 h-200 overflow-y-scroll'>
        {/* Product Grid */}
        <Grid container spacing={2} justifyContent='center'>
          {paginatedProducts.map((item) => (
            <Stack item size={{ xs: 12, sm: 6 }} md={4} key={item} width={{sm:400, md: 300}} justifyItems='center'>
              <Card>
                <CardMedia
                    component="img"
                    height="140"
                    image={productData.image}
                    alt="product"
                />
                <CardContent>
                    <Typography variant="p">{productData.category}</Typography>
                    <Link to={`/products/${productData.id}`}>
                      <Typography variant="h6">{productData.product_name}</Typography>
                    </Link>
                    <Typography variant="h4" marginTop={1} marginBottom={1} textAlign='end' fontWeight='bold'>₦{productData.price}</Typography>
                    <Stack direction='row' justifyContent='space-between' paddingRight={1}>
                        <Typography variant="p">{productData.quantity} PCS</Typography>
                        <div className='w-20 justify-end'>
                            <PrimaryBtn text='+'/>
                        </div>
                    </Stack>
                </CardContent>
              </Card>
            </Stack>
          ))}
        </Grid>
      </div>

      {/* Pagination Controls */}
      <TablePagination
        component="div"
        count={products.length}
        page={page}
        onPageChange={handleChangePage}
        rowsPerPage={rowsPerPage}
        onRowsPerPageChange={handleChangeRowsPerPage}
        rowsPerPageOptions={[6, 9, 12, 24]}
      />
    </Box>
  );
};

export default ProductCards