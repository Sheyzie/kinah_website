import { Container, Grid, Paper, Stack } from '@mui/material';
import { List, ListItem, ListItemText } from '@mui/material';
import ProductCards from './ProductCards';
import ProductFilters from './ProductFilters';


const Sidebar = () => (
  <List>
    <ListItem button>
      <ListItemText primary="Electronics" />
    </ListItem>
    <ListItem button>
      <ListItemText primary="Clothing" />
    </ListItem>
    <ListItem button>
      <ListItemText primary="Shoes" />
    </ListItem>
  </List>
);

export default function ProductsList(){
    return (
        <>
        <section className='mb-10'>
            <Container maxWidth="xl">
                <Stack direction='row' spacing={1}>
                
                    {/* Sidebar */}
                    {/* <Grid item xs={12} md={3} wrap='nowrap' flexShrink='0'>
                        <Paper elevation={3} sx={{ p: 2, borderRadius: 3, width: { xs: 150, md: 150, xl: 200 }}}>
                            <Sidebar />
                        </Paper>
                    </Grid> */}

                    {/* Product List */}
                    <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%'}}>
                            <Stack spacing={2} marginBottom={2}>
                                <h3 className='font-bold'>Product List</h3>
                                <p className='text-[#A3A3A6]'>Track stock level, availability and restocking needs in real-time</p>
                            </Stack>
                            {/* Filters */}
                            <ProductFilters />
                            <ProductCards />
                        </Paper>
                    </Grid>

                </Stack>
            </Container>
        </section>
        </>
    )
}

