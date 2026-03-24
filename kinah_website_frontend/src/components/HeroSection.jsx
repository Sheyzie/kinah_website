import { Container, Stack } from "@mui/material";
import { PrimaryBtn } from "./Buttons";
import bannerImage from "../assets/banner_image.png"

export default function HeroSection() {
    return (
        <>
            <section className="w-full my-20">
                <Container maxWidth='xl'>
                    <div className="h-fit sm:h-80 w-full p-8 bg-transparent sm:bg-[#E9D0D8] rounded-2xl block sm:flex justify-between align-middle">
                        <div className="">
                            <div className="hidden sm:block max-w-80 md:max-w-100 lg:max-w-200  bottom-0">
                                <Stack>
                                    <h1 className="text-xl sm:text-3xl font-normal">Let Your Fashion Speak  Words Greater than
                                        <span className="block my-6 text-7xl text-(--primary-color) font-(family-name:--styled-text_family) font-normal">" Demure "</span>
                                    </h1>
                                    <div className="w-full flex lg:h-20">
                                        <PrimaryBtn text='Shop Now' action={()=> console.log('clicked')} />
                                    </div>
                                </Stack>
                            </div>
                        </div>
                        <div className="relative h-full w-full sm:w-fit sm:h-65">
                            <img className="w-full h-fit sm:w-fit sm:h-full object-contain" src={bannerImage} alt="" />
                            <div className="absolute block sm:hidden bg-[#e9d0d8ab] backdrop-blur-xs p-5 rounded-2xl max-w-70 bottom-0">
                                <Stack>
                                    <h1 className="text-lg font-normal">Let Your Fashion Speak  Words Greater than
                                        <span className="block my-4 text-4xl text-(--primary-color) font-(family-name:--styled-text_family) font-normal">" Demure "</span>
                                    </h1>
                                    <div className="w-full flex lg:h-20">
                                        <PrimaryBtn text='Shop Now' action={()=> console.log('clicked')} />
                                    </div>
                                </Stack>
                            </div>
                        </div>
                    </div>
                </Container>
            </section>
        </>
    )
}