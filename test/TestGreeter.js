const Greeter = artifacts.require("Greeter");

contract("Greeter", (accounts) => {
  it("Greeter", async () => {
    const instance = await Greeter.deployed('hello world');
    let text = await instance.greet()
    console.log(text)
  })
})
