import { Paper, Stack, Table, TableBody, TableCell, TableContainer, TableHead, TableRow } from "@mui/material"
import { formatDateString } from "../helpers/orderHelper"
import { formatToCurrency } from "../utils/formatToCurrency"
import { Link } from "react-router"


export default function OrdersBanner({ orders }) {
    return (
        <>
        <Paper elevation={3} sx={{ p: 3, borderRadius: 3, width: '100%', height: 'fit-content'}}>
            <Stack spacing={3}>
                <h2 className="font-bold">My Orders</h2>

                {orders.length > 0 ? (
                    <TableContainer component={Paper} sx={{ maxHeight: 400 }}>
                        <Table stickyHeader aria-label="spanning table">
                            <TableHead>
                                <TableRow>
                                    <TableCell>Order No.</TableCell>
                                    <TableCell align="right">No. of items</TableCell>
                                    <TableCell align="right">Amount</TableCell>
                                    <TableCell align="right">Status</TableCell>
                                    <TableCell align="right">Date</TableCell>
                                </TableRow>
                            </TableHead>
                            <TableBody>
                                {orders.map((order, index) => (
                                    <TableRow key={order.id + index}>
                                        <TableCell sx={{color: 'var(--primary-color)'}}><Link to={`/orders/${order.id}`}>#{order.order_number}</Link></TableCell>
                                        <TableCell align="right">{order.item_count}</TableCell>
                                        <TableCell align="right">{formatToCurrency(order.total_amount)}</TableCell>
                                        <TableCell align="right">{order.status}</TableCell>
                                        <TableCell align="right">{formatDateString(order.created_at)}</TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </TableContainer>
                ) : 
                <p>You don't have any order yet.</p>}
            </Stack>
        </Paper>
        </>
    )
}