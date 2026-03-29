import {
  Stack,
  TextField,
  MenuItem,
  Button
} from "@mui/material";

const ProductFilters = () => {
  return (
    <Stack
      direction={{ xs: "column", sm: "row" }}
      spacing={2}
      mb={3}
      alignItems={{ xs: "stretch", sm: "center" }}
    >

      {/* Type */}
      <TextField
        select
        label="Type"
        size="small"
        defaultValue='all'
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="all">All</MenuItem>
        <MenuItem value="shirt">Shirt</MenuItem>
        <MenuItem value="jersey">Jersey</MenuItem>
      </TextField>

      {/* Search */}
      <TextField
        select
        label="Category"
        variant="outlined"
        size="small"
        defaultValue='all'
        sx={{ minWidth: 150 }}
      >
        <MenuItem value='all'>All</MenuItem>
        <MenuItem value='men'>Men</MenuItem>
        <MenuItem value='women'>Women</MenuItem>
        <MenuItem value='unisex'>Unisex</MenuItem>
        <MenuItem value='kids'>Kids</MenuItem>
      </TextField>

      {/* Sort */}
      <TextField
        select
        label="Sort By"
        size="small"
        defaultValue='default'
        sx={{ minWidth: 150 }}
      >
        <MenuItem value="default">-- default</MenuItem>
        <MenuItem value="priceLow">Price: Low to High</MenuItem>
        <MenuItem value="priceHigh">Price: High to Low</MenuItem>
      </TextField>

      {/* Button */}
      {/* <Button variant="contained">
        Apply
      </Button> */}
    </Stack>
  );
};

export default ProductFilters;