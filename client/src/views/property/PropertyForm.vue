<template>
  <div class="property-form">
    <div class="flex flex-row justify-between w-4/5">
      <div class="heading-1">Create New Property</div>
      <div>
        <el-button @click="saveForm()" type="success" plain size="medium"
          >Save</el-button
        >
        <el-button
          type="warning"
          plain
          @click="routeToPropertyList()"
          size="medium"
          >Cancel</el-button
        >
      </div>
    </div>
    <el-form
      label-position="top"
      class="w-4/5"
      :rules="formRules"
      :model="formModel"
      ref="property-form"
    >
      <el-form-item class="mt-10 mb-10 w-full" label="Name" prop="name">
        <el-input v-model="formModel.name" class="w-full"></el-input>
      </el-form-item>
      <el-form-item class="mt-10 mb-10 w-full" label="Price" prop="price">
        <el-input
          type="number"
          v-model="formModel.price"
          class="w-full"
        ></el-input>
      </el-form-item>
      <el-form-item class="mt-10 mb-10" label="Description" prop="description">
        <el-input
          type="textarea"
          :autosize="{ minRows: 2, maxRows: 4 }"
          v-model="formModel.description"
        ></el-input>
      </el-form-item>
    </el-form>
  </div>
</template>
<script>
import axios from "axios";
export default {
  data: () => ({
    formModel: {
      name: null,
      description: null,
      price: null,
    },
    formRules: {
      name: [{ required: true, message: "Please input name", trigger: "blur" }],
      price: [
        { required: true, message: "Please input price", trigger: "blur" },
      ],
      description: [
        {
          required: true,
          message: "Please input description",
          trigger: "blur",
        },
      ],
    },
  }),
  methods: {
    routeToPropertyList() {
      this.$router.push({ name: "PropertyList" });
    },
    async saveForm() {
      let propertyModel = this.$_.clone(this.formModel);
      let valid = await this.$refs["property-form"].validate();
      if (valid) {
        try {
          let response = await axios.post(
            "http://localhost:5000/addNewProperty",
            { property: propertyModel }
          );
          if (response) {
            this.routeToPropertyList();
          }
        } catch (error) {
          this.$message.error("Server Error");
        }
      } else {
        this.$message.error("Error Occurred");
        return false;
      }
    },
  },
};
</script>
