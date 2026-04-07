import { useSelector } from "react-redux"
import { dataProvider } from "../providers/dataProvider"


export async function createOrder(data) {    
    console.log(data)
    const order = dataProvider.create('orders', data)
    return {success: true, message: 'Success', order}
}

export const extractAddress = (place) => {
    const addressData = place.address
    const formatedAddress = {
        place_id: place.place_id,
        country: addressData.country,
        city: addressData.city || addressData.county,
        state: addressData.state.replace(/state/gi, "").trim(),
        display_name: place.display_name,
        longitude: place.lon,
        latitude: place.lat
    }

    return formatedAddress
}

function getEstimatedDeliveryDate(travelSeconds) {
    const now = new Date();

    // buffers (in minutes)
    const pickupBuffer = 20;
    const trafficBuffer = 30;
    const dropoffBuffer = 10;

    const totalSeconds =
        travelSeconds +
        (pickupBuffer + trafficBuffer + dropoffBuffer) * 60;

    const deliveryDate = new Date(now.getTime() + totalSeconds * 1000);

    return deliveryDate.toUTCString();
}

export async function getDistanceKm(from, to) {
    const API_KEY = import.meta.env.VITE_GEOAPIFY_API_KEY;

    const url = `https://api.geoapify.com/v1/routematrix?apiKey=${API_KEY}`;

    const body = {
        mode: "drive",
        sources: [{ location: from }],       // [lon, lat]
        targets: [{ location: to }]
    };

    try {
        const res = await fetch(url, {
            method: "POST",
            headers: {
            "Content-Type": "application/json"
            },
            body: JSON.stringify(body)
        });

        const data = await res.json();

        // distance is in meters
        const { distance, time } = data.sources_to_targets[0][0];

        const kilometers = distance / 1000
        const deliveryDate = getEstimatedDeliveryDate(time)
        return { kilometers, deliveryDate }
    }
    catch (err) {
        throw err
    }
}

export function formatDeliveryDate(date) {
    const day = date.getDate();
    const year = date.getFullYear();
    
    const months = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ];
    const month = months[date.getMonth()];

    function getSuffix(d) {
        if (d >= 11 && d <= 13) return "th";
        switch (d % 10) {
        case 1: return "st";
        case 2: return "nd";
        case 3: return "rd";
        default: return "th";
        }
    }

    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, "0");
    const ampm = hours >= 12 ? "PM" : "AM";
    hours = hours % 12 || 12; // convert to 12-hour format

    return `${day}${getSuffix(day)} ${month} ${year}, ${hours}:${minutes} ${ampm}`;
}