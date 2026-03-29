import { dataProvider } from "../providers/dataProvider";
import productImage from '../assets/product_image.png'


const productData = {
    id: "4b01f7e3-3eff-4678-9197-c1a952b0224b",
    name: 'Givenchy Up and Down',
    category: {
        "id": 1,
        "name": "Male",
        "color": "blue"
    },
    type: {
        "id": 1,
        "name": "Shirt",
        "color": "green"
    },
    package_type: "single",
    price: 2000,
    old_price: null,
    discount_type: "percent",
    discount_value: "10.00",
    currency: "NGN",
    description: 'This collection features Snoopy and his friends enjoying basketball in a vintage paenut Givenchy Up and Down',
    quantity: 89,
    sold: 0,
    created_at: "2026-03-29T10:37:24.340588Z",
    updated_at: "2026-03-29T10:37:24.340609Z",
    final_price: 1800.0,
    review_score: 0.0,
    images: [
        {
            id: 1,
            image: productImage,
            is_primary: true,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 2,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 3,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 4,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
        {
            id: 5,
            image: productImage,
            is_primary: false,
            created_at: "2026-03-29T10:37:24.340588Z",
        },
    ]
}

export const productLoader = async ({ params }) => {
  const { id } = params;

  try {
    // const { data } = await dataProvider.getOne({
    // resource: "products", // change to your resource
    // id,
    // });

    // return { product: data };
    return { product: productData };
  } catch (error) {
    throw new Response("Failed to fetch data", { status: 500 });
  }
};