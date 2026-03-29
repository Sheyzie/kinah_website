import { Avatar, Stack } from "@mui/material"
import StarIcon from '@mui/icons-material/Star';
import productImage from '../assets/product_image.png'

export default function ReviewCard({ review}) {
    return (
        <div className="my-5">
            <Stack direction='row' spacing={2}>
                <Avatar src={productImage} />
                <Stack >
                    <h4 className="font-bold">{review.user}</h4>
                    <Stack direction='row' spacing={1}>
                        {[...Array.from({ length: Math.min(review.rating, 5) })].map((_, i) => (
                        <StarIcon
                            key={i}
                            fontSize="small"
                            sx={{ color: "#FFC300" }}
                        />
                        ))}
                    </Stack>
                    <p>{review.comment}</p>
                </Stack>
            </Stack>
        </div>
    )
}