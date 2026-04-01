import { 
    Container, 
    Grid, 
    Paper, 
    Stack, 
    TablePagination,
    Box, } from '@mui/material';
import { List, ListItem, ListItemText } from '@mui/material';
import ProductFilters from './ProductFilters';
import { useEffect, useState } from 'react';
import ProductCard from './ProductCard';
import { useDispatch, useSelector } from "react-redux";
import { fetchProducts } from '../store/productSlice';


export default function ProductsList(){
    const dispatch = useDispatch()
    const { products, status, error } = useSelector((state) => state.products);

    const [page, setPage] = useState(0);
    const [rowsPerPage, setRowsPerPage] = useState(6);
    const [filter, setFilter] = useState({category: 'all', type: 'all'});
    const [sorter, setSorter] = useState('default');

    useEffect(() => {
        if (status === "idle") {
            const pagination = {current: page, pageSize: rowsPerPage}
            const filters = [
                {field: 'category', value: filter.category},
                {field: 'type', value: filter.type}
            ]

            let sorters = []

            if (sorter === 'default') {
                sorters = []
            } else if (sorter === 'priceLow') {
                sorters = [
                {field: 'price', order: 'asc' }
            ]
            } else {
                sorters = [
                    {field: 'price', order: 'desc' }
                ]
            }

            dispatch(fetchProducts({ pagination, filters, sorters }));
        }
    }, [status, dispatch]);

    if (status === "loading") return <p>Loading...</p>;
    if (status === "failed") return <p>Error: {error}</p>;

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
    
    return (
        <>
        <section className='mb-10'>
            <Container maxWidth="xl">
                <Stack direction='row' spacing={1}>

                    {/* Product List */}
                    <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%'}}>
                            <Stack spacing={2} marginBottom={2}>
                                <h3 className='font-bold'>Product List</h3>
                                <p className='text-[#A3A3A6]'>Track stock level, availability and restocking needs in real-time</p>
                            </Stack>
                            {/* Filters */}
                            <ProductFilters 
                                filter={filter} 
                                setFilter={setFilter}
                                sorter={sorter} 
                                setSorter={setSorter}
                                />
                            {/* <ProductCards /> */}

                            <Box>
                                <div className='p-10 h-200 overflow-y-scroll'>
                                    {/* Product Grid */}
                                    <Grid container spacing={2} justifyContent='center'>
                                    {paginatedProducts.map((product) => (
                                        <ProductCard key={product.id} product={product}/>
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
                        </Paper>
                    </Grid>

                </Stack>
            </Container>
        </section>
        </>
    )
}

