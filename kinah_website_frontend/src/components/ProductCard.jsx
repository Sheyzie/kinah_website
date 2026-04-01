import { 
    Stack, 
    Card, 
    CardContent,
    CardMedia,
    Typography, 
    Chip } from '@mui/material';
import { Link } from 'react-router';
import { useDispatch } from "react-redux";
import { addToCart } from "../store/cartSlice";
import { useState } from "react";
import { PrimaryBtn } from './Buttons';
import { formatToCurrency } from '../utils/formatToCurrency';


export default function ProductCard({ product }) {
    const [showChip, setShowChip] = useState(false);
    const dispatch = useDispatch()
    const mainImage = product.images.find(image => image.is_primary === true)

    const addProductToCart = (e) => {
        const productData = {
            id: product.id,
            name: product.name,
            type: product.type.name,
            category: product.category.name,
            package_type: product.package_type,
            price: product.final_price,
            image: mainImage.image,
        }

        setShowChip(true);

        // hide after animation
        setTimeout(() => {
            setShowChip(false);
        }, 600);

        dispatch(addToCart(productData))
    }
    
    return (
        <Stack item='true' size={{ xs: 12, sm: 6 }} md={4} width={{sm:400, md: 300}} justifyItems='center'>
            <Card>
                <CardMedia
                    component="img"
                    height="140"
                    image={mainImage.image}
                    alt="product"
                />
                <CardContent>
                    <Typography variant="p">{product.category.name}</Typography>
                    <Link to={`/products/${product.id}`}>
                        <Typography variant="h6">{product.name}</Typography>
                    </Link>
                    <Typography variant="h4" marginTop={1} marginBottom={1} textAlign='end' fontWeight='bold'>{formatToCurrency(product.price)}</Typography>
                    <Stack direction='row' justifyContent='space-between' paddingRight={1}>
                        <Typography variant="p">{product.quantity} {product.package_type === 'single' ? 'PCS' : 'PKT' }</Typography>
                        <div className='w-20 justify-end relative'>
                            {showChip && (
                                <Chip
                                label="+1"
                                // color="success"
                                className="animate-chip"
                                sx={{backgroundColor: 'pink', color: 'black', width: 60, position: "absolute", top: 0, left: '50%', transform: 'translateX(-50%)' }}
                                />
                            )}
                            <PrimaryBtn text='+' action={addProductToCart} />
                        </div>
                    </Stack>
                </CardContent>
            </Card>
        </Stack>
    )
}