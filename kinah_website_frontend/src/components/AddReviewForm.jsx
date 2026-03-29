import { Paper, Rating, Stack, TextField, Typography } from "@mui/material"
import { PrimaryBtn } from "../components/Buttons";
import { useState } from "react";


export default function AddReviewForm() {
    const [rating , setRating] = useState(0)

    return (
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack spacing={1}>
                <h3 className="font-bold">Add Review</h3>
                <Typography component="legend">Set rating</Typography>
                <Rating
                    name="rating"
                    value={rating}
                    onChange={(event, newValue) => {
                        setRating(newValue);
                    }}
                />
                <Stack direction='row' spacing={2}>
                    <TextField
                        id="comment" 
                        label='comment'
                        variant="outlined" 
                        onChange={()=> console.log('Changed')}
                        placeholder="Enter comment"
                        multiline
                        maxRows={4}
                        sx={{
                            flex: '1'
                        }}
                    />
                    <div className="w-30">
                        <PrimaryBtn text='Add Review' />
                    </div>
                </Stack>
            </Stack>
        </Paper>
    )
}