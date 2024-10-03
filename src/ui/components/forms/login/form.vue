<template>
    <Vueform size="lg">
        <StaticElement name="head">
            <h1 class="title">Login</h1>
        </StaticElement>
        <TextElement name="email" placeholder="Email" default="john@example.com" />
        <TextElement name="password" input-type="password" placeholder="Password" default="********" />
        <ButtonElement name="submit" submits>
            Submit
        </ButtonElement>
    </Vueform>
</template>
