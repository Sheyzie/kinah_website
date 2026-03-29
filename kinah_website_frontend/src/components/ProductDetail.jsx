import { Card, CardMedia, Chip, Paper, Stack } from "@mui/material"
import StarIcon from '@mui/icons-material/Star';
import { PrimaryBtn, SecondaryBtn } from "../components/Buttons";


export default function ProductDetail({ product }) {
    const mainImage = product.images.find(image => image.is_primary === true)
    const otherImages = product.images.filter(image => image.is_primary !== true)

    return (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack spacing={1}>
                <h3 className="font-bold">Product</h3>
                <p className="text-(--outline-color)">Track stock level, availability and restocking needs in real-time</p>

                <Stack direction={{xs: 'column', sm: 'row'}} spacing={2}>
                    <Stack height={'100%'} width={{xs: '100%', sm: '100%', md: 600}}>
                        <Card sx={{width: '100%'}}>
                            <CardMedia 
                                component="img"
                                width="200"
                                image={mainImage.image}
                                alt="product"
                                sx={{
                                    marginBottom: '10px'
                                }}
                            />
                            <Stack direction='row'>
                                {otherImages.map(image => (
                                    <CardMedia 
                                        key={image.id}
                                        component="img"
                                        height="140"
                                        image={image.image}
                                        alt="product"
                                    />
                                ))}
                            </Stack>
                        </Card>
                    </Stack>

                    <Stack spacing={2} minWidth={{xs: 180, sm: 250, md: 380}}>
                        <h3 className="font-bold">{product.name}</h3>
                        <div>Fitting <Chip size="small" label={product.type.name} variant="outlined" sx={{borderColor: `${product.type.color}`, color: `${product.type.color}`}} /> for <Chip size="small" label={product.category.name} variant="outlined" sx={{borderColor: `${product.category.color}`, color: `${product.category.color}`}} /></div>
                        <p>{product.description}</p>
                        <div className="font-bold flex align-middle gap-1">
                            {product.sold / 1000}K+ <span className="text-(--outline-color)">Sold</span> &middot; <StarIcon fontSize='small' sx={{color: '#FFC300'}}/> {product.review_score.toString()} <span className="text-(--outline-color)">(225 reviews)</span>
                        </div>
                        <Stack direction='row' spacing={1}>
                            <h3 className="font-bold text-3xl">₦{product.final_price}</h3>
                            <p className="text-(--outline-color) line-through opacity-60">₦{product.price}</p>
                            <p className="text-sm">save up to {product.discount_type === 'percent'? '%':'₦'}{product.discount_value}</p>
                        </Stack>
                        
                        <div className="flex flex-col gap-5">
                            {product.quantity > 0 ? 
                                <PrimaryBtn text='+ Add to Cart' /> : 
                                <Chip label='Out of stock' color="warning" sx={{height: 60, fontWeight: 700}}/>
                            }
                            
                            <SecondaryBtn text='share' />
                        </div>
                    </Stack>
                </Stack>
            </Stack>
        </Paper>
    )
}