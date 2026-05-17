import ca.pfv.spmf.algorithms.frequentpatterns.fin_prepost.PrePost;

import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;

public class SpmfBenchmarkServer {
    private static final String READY = "READY";
    private static final String BYE = "BYE";

    public static void main(String[] args) throws Exception {
        BufferedReader reader = new BufferedReader(
                new InputStreamReader(System.in, StandardCharsets.UTF_8));
        BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(System.out, StandardCharsets.UTF_8));

        writer.write(READY);
        writer.newLine();
        writer.flush();

        String line;
        while ((line = reader.readLine()) != null) {
            line = line.trim();
            if (line.isEmpty()) {
                continue;
            }

            if ("QUIT".equals(line)) {
                writer.write(BYE);
                writer.newLine();
                writer.flush();
                break;
            }

            if (!line.startsWith("RUN\t")) {
                writer.write("ERR\tUnsupported command");
                writer.newLine();
                writer.flush();
                continue;
            }

            String[] parts = line.split("\t", 5);
            if (parts.length < 5) {
                writer.write("ERR\tInvalid RUN payload");
                writer.newLine();
                writer.flush();
                continue;
            }

            String datasetPath = parts[1];
            double minsup = Double.parseDouble(parts[2]);
            String outputPath = parts[3];
            boolean usePrePostPlus = Boolean.parseBoolean(parts[4]);

            try {
                runPrePost(writer, datasetPath, minsup, outputPath, usePrePostPlus);
            } catch (Exception exception) {
                writer.write("ERR\t" + exception.getClass().getSimpleName() + "\t" + safeMessage(exception));
                writer.newLine();
                writer.flush();
            }
        }
    }

    private static void runPrePost(
            BufferedWriter writer,
            String datasetPath,
            double minsup,
            String outputPath,
            boolean usePrePostPlus) throws IOException {
        PrePost algorithm = new PrePost();
        algorithm.setUsePrePostPlus(usePrePostPlus);

        long startNanos = System.nanoTime();
        algorithm.runAlgorithm(datasetPath, minsup, outputPath);
        long elapsedNanos = System.nanoTime() - startNanos;

        writer.write("OK\t" + elapsedNanos);
        writer.newLine();
        writer.flush();
    }

    private static String safeMessage(Exception exception) {
        String message = exception.getMessage();
        return message == null ? "" : message.replace('\n', ' ').replace('\r', ' ');
    }
}
