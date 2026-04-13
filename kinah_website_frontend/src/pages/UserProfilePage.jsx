import { Chip, Container, Divider, Grid, IconButton, Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { useEffect, useRef, useState } from "react";
import placeholderImage from '../assets/man.jpg'
import { useSelector } from "react-redux";
import { Link, useNavigate } from "react-router";
import { PrimaryBtn } from "../components/Buttons";
import EditIcon from '@mui/icons-material/Edit';
import { formatToCurrency } from "../utils/formatToCurrency";
import { formatDateString } from "../helpers/orderHelper";
import ProfileImageBanner from "../components/ProfileImageBanner";
import PersonalInfoBanner from "../components/PersonalInfoBanner";
import AddressBanner from "../components/AddressBanner";
import OrdersBanner from "../components/OrdersBanner";

function UserProfilePage(){
    const user = useSelector(state => state.user.user)
    const navigate = useNavigate()
    useEffect(() => {
        if(!user.isLoggedIn) {
            navigate('/auth/login')
        }
    }, [user])
    console.log(user)
    

    const orders = [
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
        {
            id: "8f68013b-6ba5-4fad-a93d-9763c238aae6",
            order_number: "ORD-000001",
            user: "f389450d-ef88-40a9-8fbf-3ce64e37f483",
            user_email: "testuser@example.com",
            user_full_name: "Test User",
            status: "pending",
            payment_status: "pending",
            payment_method: "paystack",
            total_amount: "0.00",
            item_count: 0,
            created_at: "2026-04-13T13:42:38.147565Z"
        },
    ]

    return (
        <>
        <section className='mb-10 mt-25'>
            <Container maxWidth="xl">
                <Grid size={{ xs: 12, sm: 6 , md: 9}} width='100%'>
                    <Stack spacing={5}>
                        
                        <ProfileImageBanner user={user} />

                        <PersonalInfoBanner userData={user} />

                        {user.billing_address && (
                            <AddressBanner addressData={user.billing_address} />
                        )}

                        {user.shipping_address && (
                            <AddressBanner addressData={user.shipping_address} />
                        )}

                        <OrdersBanner orders={orders} />
                    </Stack> 
                </Grid>
            </Container>
        </section>
        </>
    )
}

export default UserProfilePage