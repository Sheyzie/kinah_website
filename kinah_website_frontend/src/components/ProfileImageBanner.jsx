import { Chip, IconButton, Paper, Stack } from "@mui/material"
import CameraAltIcon from '@mui/icons-material/CameraAlt';
import DeleteIcon from '@mui/icons-material/Delete';
import ProfileImageUploader from "./ProfileImageUploader"
import placeholderImage from '../assets/man.jpg'
import { useRef, useState } from "react";

export default function ProfileImageBanner({ user }) {
    const initialImage = user.pohoto || placeholderImage
    const [image, setImage] = useState(initialImage || null);
    const fileInputRef = useRef(null);

    const handleImageChange = (file) => {
        console.log("Selected file:", file);
        // upload to server here
    };

    const handleImageRemove = () => {
        setImage(placeholderImage);
        setProgress(0);
        setUploading(false);

        if (onUpload) {
            onUpload(null);
        }
    };

    return (
        <>
        <Paper 
            elevation={3} 
            sx={{
                p: 3,
                borderRadius: 3,
                width: "100%",
                height: "fit-content",

                background: {
                xs: "linear-gradient(to right, white 80%, var(--primary-color) 100%)", // mobile
                sm: "linear-gradient(to right, white 35%, var(--primary-color) 100%)",
                md: "linear-gradient(to right, white 20%, var(--primary-color) 100%)",
                },
            }}
        >
            <h2 className="font-bold mb-5">My Profile</h2>
            <Stack direction='row' spacing={5} alignItems='center'>
                <div className="relative w-fit">
                    <ProfileImageUploader image={image} setImage={setImage} onChange={handleImageChange} fileRef={fileInputRef} />
                    {/* Upload Button */}
                    <div className="upload-button">
                        <IconButton
                            aria-label="change profile pic"
                            onClick={() => fileInputRef.current.click()}
                        >
                            <CameraAltIcon />
                        </IconButton>
                    </div>

                    {/* Remove Button */}
                    {image && image != placeholderImage && (
                        <div className="remove-button">
                            <IconButton
                                aria-label="delete" 
                                color="error"
                                onClick={handleImageRemove}
                            >
                                <DeleteIcon />
                            </IconButton>
                        </div>
                    )}
                </div>

                <Stack spacing={1}>
                    <h2 className="font-bold text-2xl">{user.first_name} {user.last_name}</h2>
                    <Chip 
                        label={user.role.role_name} 
                        size="small" 
                        variant="outlined"
                        sx={{width: 'fit-content', borderColor: user.role.color, color: user.role.color}}
                    />
                    <address>{user.shipping_address?.state}, {user.shipping_address?.country}</address>
                </Stack>
            </Stack>
        </Paper>
        </>
    )
}