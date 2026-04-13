import { Paper, Stack, TextField } from "@mui/material"
import { PrimaryBtn } from "../components/Buttons";
import EditIcon from '@mui/icons-material/Edit';
import SaveIcon from '@mui/icons-material/Save';
import { useState } from "react";


export default function PersonalInfoBanner({ userData }){
    const [editMode, setEditMode] = useState(false)
    const [user, setUser] = useState(userData)

    const handleEdit = (e) => {
        setEditMode(true)
        console.log('Handled')
    }

    const handleSave = (e) => {
        console.log('Handled')
        setEditMode(false)
    }
    
    
    return (
        <>
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack spacing={3}>
                <div className="flex justify-between">
                    <h2 className="font-bold">Personal Information</h2>

                    <div className="w-25">
                        {editMode ? 
                            <PrimaryBtn text='Save' EndIcon={SaveIcon} action={handleSave} />:
                            <PrimaryBtn text='Edit' EndIcon={EditIcon} action={handleEdit} />
                        }
                    </div>
                </div>
                <hr className="opacity-45" />

                <Stack spacing={3} direction={{xs: 'column', sm: 'column', md: 'row'}} justifyContent='space-between'>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">FIRST NAME</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={user.first_name} onChange={(e) => setUser(prevUser => ({...prevUser, first_name: e.target.value}))} /> : 
                            <h3 className="text-xl">{user.first_name}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">LAST NAME</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={user.last_name} onChange={(e) => setUser(prevUser => ({...prevUser, last_name: e.target.value}))} /> : 
                            <h3 className="text-xl">{user.last_name}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">EMAIL</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={user.email} onChange={(e) => setUser(prevUser => ({...prevUser, email: e.target.value}))} /> : 
                            <h3 className="text-xl">{user.email}</h3>
                        }
                    </div>
                    <div>
                        <h3 className="text-sm text-(--outline-color) font-bold">PHONE</h3>
                        {editMode ? 
                            <TextField variant="outlined" value={user.phone} onChange={(e) => setUser(prevUser => ({...prevUser, phone: e.target.value}))} /> : 
                            <h3 className="text-xl">{user.phone}</h3>
                        }
                    </div>
                </Stack>
            </Stack>
        </Paper>
        </>
    )
}