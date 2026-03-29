import {Container, Grid } from "@mui/material"
import { useLoaderData } from "react-router-dom";
import ProductDetail from "../components/ProductDetail";
import ProductReview from "../components/ProductReview";
import AddReviewForm from "../components/AddReviewForm";


function ProductPage(){
    const { product } = useLoaderData();
    
    return (
        <>
        <section className='mb-10 mt-25'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    
                    <div className="mb-10">
                        <ProductDetail product={product}/>
                    </div>

                    <div className="mb-10">
                        <ProductReview />
                    </div>

                    <div>
                        <AddReviewForm />
                    </div>
                </Grid>
            </Container>
        </section>
        </>
    )
}

export default ProductPage