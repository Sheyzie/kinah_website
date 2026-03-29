import { MenuItem, Paper, Stack, TextField } from "@mui/material"
import { PrimaryBtn, SecondaryBtn } from "../components/Buttons";

import ReviewCard from "./ReviewCard";

export default function ProductReview() {
    const reviews = [
      {
        id: 1,
        user: "Test User",
        product: {
        "id": "ca55a22d-ca82-4731-a9e9-4ae0ce8876d1",
        "name": "Test Shirt",
        "image": null
        },
        rating: 3,
        comment: 'A simple design but makes the user seem neat and beautiful, the material is soft but when worn it often wrinkles because of sitting too long.',
        created_at: "2026-03-29T13:17:15.612507Z"
      },
      {
        id: 2,
        user: "Test User",
        product: {
        "id": "ca55a22d-ca82-4731-a9e9-4ae0ce8876d1",
        "name": "Test Shirt",
        "image": null
        },
        rating: 5,
        comment: 'A simple design but makes the user seem neat and beautiful, the material is soft but when worn it often wrinkles because of sitting too long.',
        created_at: "2026-03-29T13:17:15.612507Z"
      },
      {
        id: 3,
        user: "Test User",
        product: {
            id: "ca55a22d-ca82-4731-a9e9-4ae0ce8876d1",
            name: "Test Shirt",
            image: null
        },
        rating: 4,
        comment: 'A simple design but makes the user seem neat and beautiful, the material is soft but when worn it often wrinkles because of sitting too long.',
        created_at: "2026-03-29T13:17:15.612507Z"
      },
      {
        id: 4,
        user: "Test User",
        product: {
            id: "ca55a22d-ca82-4731-a9e9-4ae0ce8876d1",
            name: "Test Shirt",
            image: null
        },
        rating: 4,
        comment: 'A simple design but makes the user seem neat and beautiful, the material is soft but when worn it often wrinkles because of sitting too long.',
        created_at: "2026-03-29T13:17:15.612507Z"
      },
      {
        id: 5,
        user: "Test User",
        product: {
            id: "ca55a22d-ca82-4731-a9e9-4ae0ce8876d1",
            name: "Test Shirt",
            image: null
        },
        rating: 4,
        comment: 'A simple design but makes the user seem neat and beautiful, the material is soft but when worn it often wrinkles because of sitting too long.',
        created_at: "2026-03-29T13:17:15.612507Z"
      },
   ]
    return (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack direction='row' justifyContent='space-between'>
                <Stack >
                    <h3 className="font-bold">Reviews</h3>
                    <p className="text-(--outline-color)">Showing {reviews.length} reviews</p>
                </Stack>

                <TextField
                    select
                    label="sort"
                    size="small"
                    defaultValue='latest'
                    sx={{ minWidth: 150 }}
                >
                    <MenuItem value='latest'>Latest</MenuItem>
                    <MenuItem value='oldest'>Oldest</MenuItem>
                </TextField>
            </Stack>

            <div className="mt-10 h-100 overflow-y-scroll">
                <Stack>
                    {reviews.map(review => (
                        <div key={review.id}>
                            <ReviewCard review={review} />
                            <hr className="text-(--outline-color) opacity-60" />
                        </div>
                    ))}
                </Stack>
            </div>
        </Paper>
    )
}