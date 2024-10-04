<template>
    <Vueform :endpoint="false" size="lg">
        <StaticElement name="head">
            <h1 class="title">Login</h1>
        </StaticElement>
        <TextElement name="username" placeholder="User Name"/>
        <TextElement name="password" input-type="password" placeholder="Password" />
        <ButtonElement name="submit" submits>
            Submit
        </ButtonElement>
    </Vueform>
</template>
